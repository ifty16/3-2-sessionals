package server;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import models.ChunkInfo;
import models.FileMetadata;
import models.FileRequest;
import models.Message;

public class ServerConfig {
    public static final long MAX_BUFFER_SIZE = 1500 * 1024 * 1024; // 1500 MB
    public static final int MIN_CHUNK_SIZE = 50*1024;
    public static final int MAX_CHUNK_SIZE = 500*1024;
    public static final int SERVER_PORT = 6666;
    private static long currentBufferUsage = 0;

    public static final String SERVER_DATA_DIR = "server_data/";


    private static Map<String,ClientHandler> onlineClients = new ConcurrentHashMap<>(); //concurrent for thread safety

    //all registered client ever connnected
    public static Set<String> allClients = ConcurrentHashMap.newKeySet();
    // File metadata: fileID -> FileMetadata
    private static Map<String, FileMetadata> fileRegistry = new ConcurrentHashMap<>();
    // File requests: requestID -> FileRequest
    private static Map<String, FileRequest> fileRequests = new ConcurrentHashMap<>();
    // Ongoing uploads: fileID -> ChunkInfo
    private static Map<String, ChunkInfo> ongoingUploads = new ConcurrentHashMap<>(); //upload progress track korar jonne
    // File chunks buffer: fileID -> List of byte arrays
    private static Map<String, List<byte[]>> fileChunksBuffer = new ConcurrentHashMap<>(); //upload temp storage
    // Messages: username -> List<Message>
    private static Map<String, List<Message>> userMessages = new ConcurrentHashMap<>();
    

    //check if client is online
    public static boolean isClientOnline(String username){
        return onlineClients.containsKey(username); 
    }

    //add online client
    public static void addOnlineClient(String username, ClientHandler handler){
        onlineClients.put(username, handler);
        allClients.add(username); //set
    }

    //getter
    public static FileMetadata getFileMetadata(String fileID) {
        return fileRegistry.get(fileID);
    }
    public static Set<String> getAllClients(){
        return new HashSet<>(allClients);
    }
    public static Set<String> getOnlineClients(){
        return new HashSet<>(onlineClients.keySet());
    }
    public static List<FileMetadata> getFilesOwnedBy(String username) {
        List<FileMetadata> files = new ArrayList<>();
        for (FileMetadata metadata : fileRegistry.values()) {
            if (metadata.getOwner().equals(username)) {
                files.add(metadata);
            }
        }
        return files;
    }
    public static List<FileMetadata> getPublicFilesNotOwnedBy(String username) {
        List<FileMetadata> files = new ArrayList<>();
        for (FileMetadata metadata : fileRegistry.values()) {
            if (!metadata.getOwner().equals(username) && 
                metadata.getAccessType().equals(utils.Protocol.PUBLIC)) {
                files.add(metadata);
            }
        }
        return files;
    }
    public static FileRequest getFileRequest(String requestID) {
        return fileRequests.get(requestID);
    }

    public static synchronized void addBufferUsage(long size) {
        currentBufferUsage += size;
    }
    
    public static synchronized void removeBufferUsage(long size) {
        currentBufferUsage -= size;
    }
    
    public static synchronized long getCurrentBufferUsage() {
        return currentBufferUsage;
    }
    // Add this method to ServerConfig.java
    public static Map<String, List<byte[]>> getAllFileChunksMap() {
        return fileChunksBuffer;
    }

    public static void removeOnlineClient(String username) {
        onlineClients.remove(username);
    }
    
 




    public static synchronized boolean canAccommodateFile(long fileSize) {
        System.out.println("DEBUGGGGGG=============  current buffer usage : "+ currentBufferUsage + " , requested file size: " + fileSize + " , max buffer size: " + MAX_BUFFER_SIZE);
        return (currentBufferUsage + fileSize) <= MAX_BUFFER_SIZE;
    }

    // Generate unique IDs
    public static int counter1 = 0, counter2 = 0, counter3 = 0;
    public static String generateFileID() {
        return "FILE_" + System.currentTimeMillis() + "_" + counter1++;

    }
    
    public static String generateRequestID() {
        return "REQ_" + System.currentTimeMillis() + "_" + counter2++;
    }
    
    public static String generateMessageID() {
        return "MSG_" + System.currentTimeMillis() + "_" + counter3++;
    }



    public static void registerFile(String fileID, FileMetadata metadata) {
        fileRegistry.put(fileID, metadata);
    }

    //upload
    public static void startUpload(String fileID, ChunkInfo chunkInfo) {
        ongoingUploads.put(fileID, chunkInfo);
        fileChunksBuffer.put(fileID, new ArrayList<>());
    }
     public static void addChunk(String fileID, byte[] chunk) {
        List<byte[]> chunks = fileChunksBuffer.get(fileID);
        if (chunks != null) {
            chunks.add(chunk);
        }
    }
    public static ChunkInfo getUploadInfo(String fileID) {
        return ongoingUploads.get(fileID);
    }
    
    public static List<byte[]> getFileChunks(String fileID) {
        return fileChunksBuffer.get(fileID);
    }
    
    public static void completeUpload(String fileID) {
        ongoingUploads.remove(fileID);
        fileChunksBuffer.remove(fileID);
    }
    
    public static void cancelUpload(String fileID) {
        ChunkInfo info = ongoingUploads.remove(fileID);
        fileChunksBuffer.remove(fileID);
        if (info != null) {
            removeBufferUsage(info.getTotalSize());
        }
    }

    // Request management
    public static void addFileRequest(String requestID, FileRequest request) {
        fileRequests.put(requestID, request);
    }
    
  
    
    // Message management
    // Message management
public static void addMessage(String username, Message message) {
    userMessages.computeIfAbsent(username, k -> new ArrayList<>()).add(message);
    
    // Immediately append to file
    appendMessageToFile(username, message);
}
    
    public static List<Message> getUnreadMessages(String username) {
        List<Message> messages = userMessages.get(username);
        if (messages == null) return new ArrayList<>();
        
        List<Message> unread = new ArrayList<>();
        for (Message msg : messages) {
            if (!msg.isRead()) {
                unread.add(msg);
                msg.setRead(true);
            }
        }
        return unread;
    }

     // shob directory er name gulo allClients e add korbe
    public static void loadExistingUsers() {
        try {
            java.io.File dataDir = new java.io.File(SERVER_DATA_DIR); // directory ta open korbe
            
            // Check if directory exists
            if (!dataDir.exists() || !dataDir.isDirectory()) {
                System.out.println("No existing users found. Starting fresh.");
                return;
            }
            
            // Get all subdirectories (each represents a user)
            java.io.File[] userDirs = dataDir.listFiles(java.io.File::isDirectory); // listfiles( file -> file.isDirectory() )     
            
            if (userDirs == null || userDirs.length == 0) {
                System.out.println("No existing users found. Starting fresh.");
                return;
            }
            
            // Add each directory name to allClients
            int count = 0;
            for (java.io.File userDir : userDirs) {
                String username = userDir.getName();
                allClients.add(username);
                count++;
            }
            
            System.out.println("Loaded " + count + " existing user(s): " + allClients);
            
        } catch (Exception e) {
            System.err.println("Error loading existing users: " + e.getMessage());
            e.printStackTrace(); // prints the stack trace for debugging. stack trace = kon line e error hoise etc
        }
    }

// file list er jonne activity log theke read korbe
// age user name er list load kore nite hobe
public static void loadExistingFiles() {
    try {
        int fileCount = 0;
        
        for (String username : allClients) {
            String logPath = SERVER_DATA_DIR + username + "/activity_log.txt";
            
            java.io.File logFile = new java.io.File(logPath);
            
            if (!logFile.exists()) {
                continue;
            }
            
            // Read log file and extract successful uploads
            try (java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(logFile))) {
                String line;
                while ((line = br.readLine()) != null) { //actibity file er prottek line er jonne
                    // Parse log entry
                    // Format: [timestamp] File: name | Action: UPLOAD | Status: SUCCESS | Access: PUBLIC
                    if (line.contains("Action: UPLOAD") && line.contains("Status: SUCCESS")) {
                        String fileName = extractValue(line, "File: ", " |");  
                        String accessType = extractValue(line, "Access: ", "$");

                        // System.out.println("DEBUGGGG Extracted from log - fileName: " + fileName + ", accessType: " + accessType);
                        
                        if (fileName != null && accessType != null) {
                            // Check if file still exists on disk jeta log e pailam. dlt implement korle pore lagbe
                            String filePath = SERVER_DATA_DIR + username + "/" + fileName;
                            java.io.File file = new java.io.File(filePath);
                            
                            if (file.exists()) {
                                // Create metadata and register
                                String fileID = generateFileID();
                                FileMetadata metadata = new FileMetadata(fileName, file.length(), username, accessType.trim());
                                metadata.setFileID(fileID);
                                registerFile(fileID, metadata);
                                fileCount++;
                            }
                        }
                    }
                }
            }
        }
        
        System.out.println("Loaded " + fileCount + " existing file(s) from activity logs.");
        
    } catch (Exception e) {
        System.err.println("Error loading existing files: " + e.getMessage());
        e.printStackTrace();// getmessage = kon error hoise , stack trace = kon line e hoise
    }
}

//helper
// example line: [timestamp] File: name | Action: UPLOAD | Status: SUCCESS | Access: PUBLIC
private static String extractValue(String line, String startMarker, String endMarker) {
    try {
        int startIdx = line.indexOf(startMarker); //example: "File: " = indexof("File: ")
        if (startIdx == -1) return null;
        
        startIdx += startMarker.length(); //startIdx += 6
        
        int endIdx;
        if (endMarker.equals("$")) {
            // Extract till end of line
            endIdx = line.length();
        } else {
            endIdx = line.indexOf(endMarker, startIdx);  // endIdx = indexof(" |", search from)
            if (endIdx == -1) return null;
        }
        
        return line.substring(startIdx, endIdx).trim(); 
    } catch (Exception e) {
        return null;
    }
}


 //Appends a single message to the file immediately when created
 //format: username|||messageID|||content|||read
public static void appendMessageToFile(String username, Message msg) {
    try {
        String messagePath = SERVER_DATA_DIR + "message_history.txt";
        
        try (java.io.FileWriter fw = new java.io.FileWriter(messagePath, true); // true = append mode
             java.io.BufferedWriter bw = new java.io.BufferedWriter(fw)) {
            
            // Format: username|||messageID|||content|||read
            String line = String.format("%s|||%s|||%s|||%s%n",
                username,
                msg.getMessageID(),
                msg.getContent().replace("\n", "<NEWLINE>"), // Escape newlines
                msg.isRead()
            );
            bw.write(line);
        }
    } catch (Exception e) {
        System.err.println("Error appending message to file: " + e.getMessage());
    }
}

// Load messages from file during server startup
public static void loadMessagesFromFile() {
    try {
        String messagePath = SERVER_DATA_DIR + "message_history.txt";
        java.io.File msgFile = new java.io.File(messagePath);
        
        if (!msgFile.exists()) {
            System.out.println("No message history found. Starting fresh.");
            return;
        }
        
        int messageCount = 0;
        
        try (java.io.BufferedReader br = new java.io.BufferedReader(new java.io.FileReader(msgFile))) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] parts = line.split("\\|\\|\\|");
                
                if (parts.length == 4) {
                    String username = parts[0];
                    String messageID = parts[1];
                    String content = parts[2].replace("<NEWLINE>", "\n");
                    boolean read = Boolean.parseBoolean(parts[3]);
                    
                    // Reconstruct Message object
                    Message msg = new Message(messageID, username, content);
                    msg.setRead(read);
                    
                    // Add to userMessages
                    userMessages.computeIfAbsent(username, k -> new ArrayList<>()).add(msg); //cpmputeIfAbsent = jodi username er jonne list na thake tahole notun list create kore dibe, jodi thake tahole existing list ta return korbe
                    messageCount++;
                }
            }
        }
        
        System.out.println("Loaded " + messageCount + " message(s) from history.");
        
    } catch (Exception e) {
        System.err.println("Error loading messages: " + e.getMessage());
        e.printStackTrace();
    }
}




//Get ALL messages (read and unread) for a user

public static List<Message> getAllMessages(String username) {
    List<Message> messages = userMessages.get(username);
    if (messages == null) return new ArrayList<>();
    return new ArrayList<>(messages); // Return a copy
}


// Find existing file by owner and file name

public static String findExistingFile(String username, String fileName) {
    for (Map.Entry<String, FileMetadata> entry : fileRegistry.entrySet()) {
        FileMetadata metadata = entry.getValue();
        if (metadata.getOwner().equals(username) && 
            metadata.getFileName().equals(fileName)) {
            return entry.getKey(); // Return the fileID
        }
    }
    return null; // File not found
}

// Remove file from registry
public static void removeFile(String fileID) {
    fileRegistry.remove(fileID);
}


}
