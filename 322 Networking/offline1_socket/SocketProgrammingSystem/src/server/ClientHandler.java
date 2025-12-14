package server;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.Random;
import java.util.Set;
import models.ChunkInfo;
import models.FileMetadata;
import models.FileRequest;
import models.Message;
import utils.Protocol;

public class ClientHandler extends Thread{
    private Socket socket;
    private ObjectInputStream in;
    private ObjectOutputStream out;
    private String username;
    private boolean isAuthenticated;

    public ClientHandler(Socket socket) {
        this.socket = socket;
        this.isAuthenticated = false; // initially not logged in
    }
    
    
    @Override
public void run() {
    try {
        // Initialize input and output streams
        out = new ObjectOutputStream(socket.getOutputStream());
        in = new ObjectInputStream(socket.getInputStream());

        // authenticate
        if(!authenticate()){
            cleanup();
            return;
        }

        //main command loop
        handleClientCommands();
        
    } catch (java.io.EOFException e) {
        // Client disconnected abruptly
        System.out.println("Client disconnected abruptly: " + username);
    } catch (java.net.SocketException e) {
        // Socket closed
        System.out.println("Socket closed for client: " + username);
    } catch (IOException e) {
        System.err.println("IO error with client " + username + ": " + e.getMessage());
    } catch (Exception e) {
        System.out.println("Error in ClientHandler: " + e.getMessage());
    } finally {
        // ALWAYS cleanup, even on abrupt disconnect
        cleanup();
    }
}


    //send message to client
    private void sendMessage(String message) throws Exception {
        out.writeObject(message);
        out.flush(); // Ensure the message is sent immediately
    }

    //authenticate client by username
    private boolean authenticate() throws Exception {
        sendMessage("Enter username: ");
        String username= (String) in.readObject();

        //already online?
        if(ServerConfig.isClientOnline(username)){
            sendMessage(Protocol.DENIED + Protocol.DELIMITER + "Username already logged in. Connection denied.");
            return false;
        }

        this.username = username;
        this.isAuthenticated = true;

        ServerConfig.addOnlineClient(username, this);

        //create user directory if not exists
        FileManager.createUserDirectory(username); 

        sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + "login successful. welcome "+username +" !"); // SUCCESS:::login successful. welcome user !
        
        System.out.println("User "+ username +" logged in.");
        return true;

    }

    //cleanup resources. actions when user disconnects
    private void cleanup() {
        try {
            if (username != null) {
                //Cancel any ongoing uploads
                List<String> toCancel = new ArrayList<>();


                //kon file bad jabe
                for (String fileID : ServerConfig.getAllFileChunksMap().keySet()) {

                    FileMetadata metadata = ServerConfig.getFileMetadata(fileID); // metadata{fileID, fileName, fileSize, owner, accessType}
                    if (metadata != null && metadata.getOwner().equals(username)) {
                        toCancel.add(fileID);
                    }
                }
                

                for (String fileID : toCancel) {
                    ServerConfig.cancelUpload(fileID);
                }
                
                ServerConfig.removeOnlineClient(username);
                System.out.println("Client disconnected: " + username);
            }
            
            if (socket != null && !socket.isClosed()) {
                socket.close(); // close connection
            }
        } catch (IOException e) {
            System.err.println("Error during cleanup: " + e.getMessage());
        }
    }

    //handle client commands
private void handleClientCommands() throws Exception {
    while(isAuthenticated){
        try {
            String command = (String) in.readObject();
            
            // Check for null (client disconnected)
            if (command == null) {
                System.out.println("Received null command, client disconnected: " + username);
                break;
            }
            
            // System.out.println("Received command from " + username + ": " + command);
            processCommand(command);

        } catch (java.io.EOFException e) {
            // Client disconnected abruptly (Ctrl+C, crash, etc.)
            System.out.println("Client disconnected abruptly (EOF): " + username);
            break;
        } catch (java.net.SocketException e) {
            // Socket closed (network issue, Ctrl+C, etc.)
            System.out.println("Socket closed for client: " + username);
            break;
        } catch (Exception e) {
            System.out.println("Error processing command from " + username + ": " + e.getMessage());
            // Don't break here - only for disconnect errors
        }
    }
}

    private void processCommand(String command) throws Exception {
        //process different commands here

        String[] parts = command.split(Protocol.DELIMITER); //Protocol.UPLOAD_CHUNK + Protocol.DELIMITER + fileID + Protocol.DELIMITER + chunkBase64;
        String cmd = parts[0];

        switch (cmd) {
            case Protocol.LIST_CLIENTS:
                handleListClients();
                break;
                
            case Protocol.LIST_OWN_FILES:
                handleListOwnFiles();
                break;
                
            case Protocol.LIST_PUBLIC_FILES:
                handleListPublicFiles();
                break;
                
            case Protocol.UPLOAD_REQUEST:
                handleUploadRequest(parts);
                break;
                
            case Protocol.UPLOAD_CHUNK:  //Protocol.UPLOAD_CHUNK + Protocol.DELIMITER + fileID + Protocol.DELIMITER + chunkBase64;
                handleUploadChunk(parts);
                break;
                
            case Protocol.UPLOAD_COMPLETE: //Protocol.UPLOAD_COMPLETE + Protocol.DELIMITER + fileID
                handleUploadComplete(parts);
                break;
                
            case Protocol.DOWNLOAD_REQUEST:
                handleDownloadRequest(parts);
                break;
                
            case Protocol.MAKE_FILE_REQUEST:
                handleMakeFileRequest(parts);
                break;
                
            case Protocol.VIEW_MESSAGES:
                handleViewMessages();
                break;
                
            case Protocol.VIEW_HISTORY:
                handleViewHistory();
                break;
                
            case Protocol.LOGOUT:
                isAuthenticated = false;

                break;
                
            default:
                sendMessage(Protocol.ERROR + Protocol.DELIMITER + "Unknown command");
        }

    }

    private void handleListClients() throws Exception {
        Set<String> allClients = ServerConfig.getAllClients();
        Set<String> onlineClients = ServerConfig.getOnlineClients();
        
        StringBuilder response = new StringBuilder(Protocol.SUCCESS + Protocol.DELIMITER);
        response.append("\n\n=== ALL CLIENTS ===\n");
        
        for (String client : allClients) {
            String status = onlineClients.contains(client) ? "*[ONLINE]" : "[OFFLINE]";
            response.append(client).append(" ").append(status).append("\n");
        }
        
        sendMessage(response.toString()); 
    }

    private void handleListOwnFiles() throws Exception {
        List<FileMetadata> files = ServerConfig.getFilesOwnedBy(username);
        
        StringBuilder response = new StringBuilder(Protocol.SUCCESS + Protocol.DELIMITER);
        response.append("=== YOUR FILES ===\n");
        
        if (files.isEmpty()) {
            response.append("No files uploaded yet.\n");
        } else {
            for (FileMetadata file : files) {
                response.append(file.getFileName())
                       .append(" [").append(file.getAccessType()).append("]")
                       .append(" (").append(file.getFileSize()).append(" bytes)\n");
            }
        }
        
        sendMessage(response.toString());
    }
    private void handleListPublicFiles() throws Exception {
        List<FileMetadata> files = ServerConfig.getPublicFilesNotOwnedBy(username);
        
        StringBuilder response = new StringBuilder(Protocol.SUCCESS + Protocol.DELIMITER);
        response.append("=== PUBLIC FILES FROM OTHER USERS ===\n");
        
        if (files.isEmpty()) {
            response.append("No public files available.\n");
        } else {
            for (FileMetadata file : files) {
                response.append(file.getOwner()).append("/")
                       .append(file.getFileName())
                       .append(" (").append(file.getFileSize()).append(" bytes)\n");
            }
        }
        
        sendMessage(response.toString());
    }
    private void handleUploadRequest(String[] parts) throws Exception {
    String fileName = parts[1];
    long fileSize = Long.parseLong(parts[2]);
    String accessType = parts[3];
    String requestID = parts.length > 4 ? parts[4] : null;
    
    // Check if request ID provided and valid
    if (requestID != null && !requestID.equals("null")) {
        FileRequest request = ServerConfig.getFileRequest(requestID);
        if (request == null) {
            sendMessage(Protocol.ERROR + Protocol.DELIMITER + "Invalid request ID");
            return;
        }
        // Force public access for requested files
        accessType = Protocol.PUBLIC;
    }
    
    // Check if file already exists for this user
    String existingFileID = ServerConfig.findExistingFile(username, fileName);
    
    if (existingFileID != null) {
        // File exists - update metadata instead of creating new
        FileMetadata existingMetadata = ServerConfig.getFileMetadata(existingFileID);
        
        // Check if file size changed (re-upload with different content)
        if (existingMetadata.getFileSize() != fileSize) {
            // Size changed - need to re-upload
            // Check buffer capacity for the NEW size
            if (!ServerConfig.canAccommodateFile(fileSize)) {
                sendMessage(Protocol.BUFFER_FULL + Protocol.DELIMITER + "Server buffer is full. Please try later.");
                return;
            }
        } else {
            // Same file, just updating access type
            existingMetadata.setAccessType(accessType);
            sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + "File access type updated to " + accessType);
            FileManager.logActivity(username, fileName, "UPDATE", "SUCCESS", accessType);
            return;
        }
    }
    
    // Check buffer capacity for NEW uploads
    if (!ServerConfig.canAccommodateFile(fileSize)) {
        sendMessage(Protocol.BUFFER_FULL + Protocol.DELIMITER + "Server buffer is full. Please try later.");
        return;
    }
    
    // Generate random chunk size
    Random random = new Random();
    int chunkSize = ServerConfig.MIN_CHUNK_SIZE + random.nextInt(ServerConfig.MAX_CHUNK_SIZE - ServerConfig.MIN_CHUNK_SIZE + 1);
    
    // Generate or reuse file ID
    String fileID;
    if (existingFileID != null) {
        // Re-uploading existing file with new content
        fileID = existingFileID;
        // Remove old entry before creating new one
        ServerConfig.removeFile(existingFileID);
    } else {
        // Brand new file
        fileID = ServerConfig.generateFileID();
    }
    
    // Create metadata
    FileMetadata metadata = new FileMetadata(fileName, fileSize, username, accessType);
    metadata.setFileID(fileID);
    metadata.setRequestID(requestID);
    ServerConfig.registerFile(fileID, metadata);
    
    // Initialize upload tracking
    ChunkInfo chunkInfo = new ChunkInfo(fileID, chunkSize, fileSize);
    ServerConfig.startUpload(fileID, chunkInfo);
    ServerConfig.addBufferUsage(fileSize);
    
    // Send confirmation
    sendMessage(Protocol.UPLOAD_CONFIRMED + Protocol.DELIMITER + fileID + Protocol.DELIMITER + chunkSize);
    
    System.out.println("Upload initiated for " + fileName + " by " + username + 
                      (existingFileID != null ? " (re-upload)" : " (new file)"));
}
    
    //Handles UPLOAD_CHUNK - receives a single chunk
    //Format: UPLOAD_CHUNK|||fileID|||chunkData(base64)
    private void handleUploadChunk(String[] parts) throws Exception {
        String fileID = parts[1];
        String chunkDataBase64 = parts[2];
        
        // Decode chunk data
        byte[] chunkData = Base64.getDecoder().decode(chunkDataBase64);
        
        // Store chunk
        ServerConfig.addChunk(fileID, chunkData);
        
        // Update chunk info
        ChunkInfo info = ServerConfig.getUploadInfo(fileID);
        if (info != null) {
            info.incrementReceivedChunks(); // new chunk add hoise so count++ for tracking 
        }
        
        // Send acknowledgment
        sendMessage(Protocol.CHUNK_ACK + Protocol.DELIMITER + fileID);
    }
    
     //Handles UPLOAD_COMPLETE - finalizes upload
     //Format: UPLOAD_COMPLETE|||fileID
     
    private void handleUploadComplete(String[] parts) throws Exception {
        String fileID = parts[1];
        
        FileMetadata metadata = ServerConfig.getFileMetadata(fileID);
        List<byte[]> chunks = ServerConfig.getFileChunks(fileID);
        
        if (metadata == null || chunks == null) {
            sendMessage(Protocol.ERROR + Protocol.DELIMITER + "Upload data not found");
            return;
        }
        
        // Verify file size
        long totalSize = 0;
        for (byte[] chunk : chunks) {
            totalSize += chunk.length;
        }
        
        if (totalSize != metadata.getFileSize()) {
            sendMessage(Protocol.ERROR + Protocol.DELIMITER + "File size mismatch. Upload failed.");
            FileManager.logActivity(username, metadata.getFileName(), "UPLOAD", "FAILED", metadata.getAccessType());
            ServerConfig.cancelUpload(fileID);
            return;
        }
        
        // Save file to disk
        boolean saved = FileManager.saveFile(username, metadata, chunks);
        
        if (saved) {
            sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + "Upload successful!");
            FileManager.logActivity(username, metadata.getFileName(), "UPLOAD", "SUCCESS", metadata.getAccessType());
            
            // If this was in response to a request, notify requester
            if (metadata.getRequestID() != null) {
                notifyFileRequestFulfilled(metadata);
            }
        } else {
            sendMessage(Protocol.ERROR + Protocol.DELIMITER + "Failed to save file");
            FileManager.logActivity(username, metadata.getFileName(), "UPLOAD", "FAILED", metadata.getAccessType());
        }
        
        // Cleanup
        ServerConfig.completeUpload(fileID);
        ServerConfig.removeBufferUsage(metadata.getFileSize());
    }
    
    /**
     * Handles DOWNLOAD_REQUEST
     * Format: DOWNLOAD_REQUEST|||owner|||fileName
     */
    private void handleDownloadRequest(String[] parts) throws Exception {
        String owner = parts[1];
        String fileName = parts[2];
        
        // Read file from disk
        byte[] fileData = FileManager.readFile(owner, fileName);
        
        if (fileData == null) {
            sendMessage(Protocol.ERROR + Protocol.DELIMITER + "File not found");
            FileManager.logActivity(username, fileName, "DOWNLOAD", "FAILED","N/A");
            return;
        }
        
        // Send download start
        sendMessage(Protocol.DOWNLOAD_START + Protocol.DELIMITER + fileName + Protocol.DELIMITER + fileData.length);
        
        // Send file in chunks
        int chunkSize = ServerConfig.MAX_CHUNK_SIZE; // use max chunk size for download
        int offset = 0;
        
        while (offset < fileData.length) {
            int length = Math.min(chunkSize, fileData.length - offset);
            byte[] chunk = Arrays.copyOfRange(fileData, offset, offset + length);
            String chunkBase64 = Base64.getEncoder().encodeToString(chunk);
            
            sendMessage(chunkBase64);
            offset += length;
        }
        
        // Send completion
        sendMessage(Protocol.DOWNLOAD_COMPLETE + Protocol.DELIMITER + fileName);
        FileManager.logActivity(username, fileName, "DOWNLOAD", "SUCCESS","N/A");
        
        System.out.println("Download completed: " + fileName + " for " + username);
    }
    
    
     //Format: MAKE_FILE_REQUEST|||description|||recipient
     
    private void handleMakeFileRequest(String[] parts) throws Exception {
        String description = parts[1];
        String recipient = parts[2];
        
        String requestID = ServerConfig.generateRequestID();
        FileRequest request = new FileRequest(requestID, username, recipient, description);
        ServerConfig.addFileRequest(requestID, request);
        
        // Send request to recipient(s)
        if (recipient.equals("ALL")) {
            // Broadcast to all clients
            Set<String> allClients = ServerConfig.getAllClients();
            for (String client : allClients) {
                if (!client.equals(username)) {
                    String msgContent = "File request from " + username + 
                                      ": " + description + " [Request ID: " + requestID + "]";
                    Message msg = new Message(ServerConfig.generateMessageID(), client, msgContent);
                    ServerConfig.addMessage(client, msg);
                }
            }
            sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + 
                       "Request broadcast to all users. Request ID: " + requestID);
        } else {
            // Send to specific user
            String msgContent = "File request from " + username + 
                              ": " + description + " [Request ID: " + requestID + "]";
            Message msg = new Message(ServerConfig.generateMessageID(), recipient, msgContent);
            ServerConfig.addMessage(recipient, msg);
            sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + 
                       "Request sent to " + recipient + ". Request ID: " + requestID);
        }
    }
    
    
 // Handles VIEW_MESSAGES - shows all messages with unread indicator
private void handleViewMessages() throws Exception {
    List<Message> allMessages = ServerConfig.getAllMessages(username);
    
    StringBuilder response = new StringBuilder(Protocol.SUCCESS + Protocol.DELIMITER);
    response.append("=== ALL MESSAGES ===\n");
    
    if (allMessages.isEmpty()) {
        response.append("No messages.\n");
    } else {
        for (Message msg : allMessages) {
            String indicator = msg.isRead() ? "   " : " * "; // Star for unread
            response.append(indicator).append(msg.getContent()).append("\n");
            
            // Mark as read after viewing
            if (!msg.isRead()) {
                msg.setRead(true);
            }
        }
        response.append("\n(* = unread messages)\n");
    }
    
    sendMessage(response.toString());
}
    
    
    private void handleViewHistory() throws Exception {
        String history = FileManager.readActivityLog(username);
        sendMessage(Protocol.SUCCESS + Protocol.DELIMITER + history);
    }
    
    
    private void notifyFileRequestFulfilled(FileMetadata metadata) {
        FileRequest request = ServerConfig.getFileRequest(metadata.getRequestID());
        if (request == null) return;
        
        String requester = request.getRequester();
        String msgContent = username + " has uploaded a file in response to your request: " +
                          metadata.getFileName() + " [Request ID: " + request.getRequestID() + "]";
        
        Message msg = new Message(ServerConfig.generateMessageID(), requester, msgContent);
        ServerConfig.addMessage(requester, msg);
    }

    
}

