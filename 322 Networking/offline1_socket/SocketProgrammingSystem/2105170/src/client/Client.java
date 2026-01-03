package client;

import java.io.ByteArrayOutputStream;  
import java.io.File;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Base64;
import java.util.Scanner;
import utils.Protocol;

public class Client {
    private Socket socket;
    private ObjectInputStream in;
    private ObjectOutputStream out; 
    private String username;
    private Scanner scanner;

    public Client(){
        scanner = new Scanner(System.in);
    }

    public boolean connect(String host, int port){
        try {
            socket = new Socket(host, port); //localhost fore own machine er port 6666
            out = new ObjectOutputStream(socket.getOutputStream());
            in = new ObjectInputStream(socket.getInputStream());

            System.out.println("Connected to server at " + host + ":" + port);

            // Authentication
            String message = (String) in.readObject(); // "Enter your username:"
            System.out.println(message); 

            username = scanner.nextLine().trim();
            out.writeObject(username);
            out.flush();

            String response = (String) in.readObject(); // SUCCESS|||login succesful
            String[] parts = response.split(Protocol.DELIMITER);


            // System.out.println("here" + " response is " + response + " parts[0] " + parts[0]);
            if(parts[0].equals(Protocol.SUCCESS)){
                System.out.println(parts[1]); // Welcome message
                return true;
            }else if(parts[0].equals(Protocol.DENIED)){
                System.out.println("Connection failed: " + parts[1]);
                return false;
            }
            
            
        } catch (Exception e) {
            System.out.println("Connection error: " + e.getMessage());
            return false;
        }

        return false;
    }

    //menu

    public void run(){
        System.out.println("-- -Wellcome to File Server System ---  " );
        System.out.println("username: " + username);

        boolean running = true;
        while(running){
            displayMenu();

            try {
                int choice = Integer.parseInt(scanner.nextLine().trim());
                
                switch (choice) {
                    case 1:
                        listClients();
                        break;
                    case 2:
                        listOwnFiles();
                        break;
                    case 3:
                        listPublicFiles();
                        break;
                    case 4:
                        uploadFile();
                        break;
                    case 5:
                        downloadFile();
                        break;
                    case 6:
                        makeFileRequest();
                        break;
                    case 7:
                        viewMessages();
                        break;
                    case 8:
                        viewHistory();
                        break;
                    case 9:
                        logout();
                        running = false;
                        break;
                    default:
                        System.out.println("Invalid choice. Please try again.");
                }
                
            } catch (Exception e) {
                System.out.println("Error: " + e.getMessage());
            }
        }

    }

    private void displayMenu() {
        System.out.println("\n=== MAIN MENU ===");
        System.out.println("1. List all clients");
        System.out.println("2. List my files");
        System.out.println("3. List public files");
        System.out.println("4. Upload file");
        System.out.println("5. Download file");
        System.out.println("6. Make file request");
        System.out.println("7. View messages");
        System.out.println("8. View upload/download history");
        System.out.println("9. Logout");
        System.out.print("Enter choice: ");
    }

    private void sendCommand(String command) throws Exception {
        out.writeObject(command);
        out.flush();
    }
    private String recieveResponse() throws Exception {
        String response = (String) in.readObject();
        String [] parts = response.split(Protocol.DELIMITER);
        if(parts.length > 1){
            return parts[1];
        }
        return response;
    }

    private void listClients() throws Exception {
        sendCommand(Protocol.LIST_CLIENTS);
        String response = recieveResponse();
        System.out.println("\nOnline Clients: " + response);
    }
    private void listOwnFiles() throws Exception {
        sendCommand(Protocol.LIST_OWN_FILES);
        String response = recieveResponse();
        System.out.println("\n" + response);
    }

    //Lists public files from other users
    private void listPublicFiles() throws Exception {
        sendCommand(Protocol.LIST_PUBLIC_FILES);
        String response = recieveResponse();
        System.out.println("\n" + response);
    }
    private void uploadFile() throws Exception {
        System.out.print("Enter file path to upload: ");
        String filePath = scanner.nextLine().trim();
        
        File file = new File(filePath);
        if (!file.exists() || !file.isFile()) {
            System.out.println("File not found: " + filePath);
            return;
        }
        
        System.out.print("Access type (PRIVATE/PUBLIC): ");
        String accessType = scanner.nextLine().trim().toUpperCase();
        
        if (!accessType.equals(Protocol.PRIVATE) && !accessType.equals(Protocol.PUBLIC)) {
            System.out.println("Invalid access type. Must be PRIVATE or PUBLIC.");
            return;
        }
        
        System.out.print("Is this in response to a file request? (yes/no): ");
        String isResponse = scanner.nextLine().trim().toLowerCase();
        
        String requestID = "null";
        if (isResponse.equals("yes")) {
            System.out.print("Enter request ID: ");
            requestID = scanner.nextLine().trim();
            accessType = Protocol.PUBLIC; // Force public for requested files
        }
        
        // Read file data
        byte[] fileData = Files.readAllBytes(Paths.get(filePath));
        long fileSize = fileData.length;
        String fileName = file.getName();
        
        System.out.println("\nInitiating upload for: " + fileName + " (" + fileSize + " bytes)");
        
        // Send upload request
        String uploadRequest = Protocol.UPLOAD_REQUEST + Protocol.DELIMITER + fileName + Protocol.DELIMITER + fileSize + Protocol.DELIMITER + accessType + Protocol.DELIMITER + requestID;
        sendCommand(uploadRequest);
        
        // Get response
        String response = (String) in.readObject();  //(Protocol.UPLOAD_CONFIRMED + Protocol.DELIMITER + fileID + Protocol.DELIMITER + chunkSize)
        String[] parts = response.split(Protocol.DELIMITER);  //
        
        if (parts[0].equals(Protocol.BUFFER_FULL)) {
            System.out.println("Upload denied: " + parts[1]); 
            return;
        }
        
        if (!parts[0].equals(Protocol.UPLOAD_CONFIRMED)) {
            System.out.println("Upload failed: " + response);
            return;
        }
        
        String fileID = parts[1];
        int chunkSize = Integer.parseInt(parts[2]);
        
        System.out.println("Upload confirmed. File ID: " + fileID + ", Chunk size: " + chunkSize + " bytes");
        
        // Send file in chunks
        int offset = 0; // file er kon jaga theke send korbo
        int chunkNum = 0;
        
        while (offset < fileData.length) {
            int length = Math.min(chunkSize, fileData.length - offset);
            byte[] chunk = Arrays.copyOfRange(fileData, offset, offset + length); //src, start, end
            String chunkBase64 = Base64.getEncoder().encodeToString(chunk);
            
            // Send chunk
            String chunkCommand = Protocol.UPLOAD_CHUNK + Protocol.DELIMITER + fileID + Protocol.DELIMITER + chunkBase64;
            sendCommand(chunkCommand);
            
            // Wait for acknowledgment
            String ack = (String) in.readObject(); //Protocol.CHUNK_ACK + Protocol.DELIMITER + fileID
            
            chunkNum++;
            System.out.println("Chunk " + chunkNum + " sent and acknowledged");
            
            offset += length;
        }
        
        // Send completion
        sendCommand(Protocol.UPLOAD_COMPLETE + Protocol.DELIMITER + fileID);
        
        // Get final response
        String finalResponse = (String) in.readObject();
        String[] finalParts = finalResponse.split(Protocol.DELIMITER);
        
        if (finalParts[0].equals(Protocol.SUCCESS)) {
            System.out.println(finalParts[1]);
        } else {
            System.out.println("Upload failed: " + finalParts[1]);
        }
    }


    private void downloadFile() throws Exception {
    System.out.print("Download from (enter username or 'self' for your files): ");
    String owner = scanner.nextLine().trim();
    
    if (owner.equalsIgnoreCase("self")) {
        owner = username;
    }
    
    System.out.print("Enter file name: ");
    String fileName = scanner.nextLine().trim();
    
    System.out.print("Enter download path (leave blank for current directory): ");
    String downloadPath = scanner.nextLine().trim();
    
    // Determine save location
    String savePath;
    if (downloadPath.isEmpty()) {
        // Save in current directory with original filename
        savePath = fileName;
    } else {
        // Check if path is a directory or full file path
        File pathFile = new File(downloadPath);
        
        if (pathFile.isDirectory() || downloadPath.endsWith("/") || downloadPath.endsWith("\\")) {
            // It's a directory - append filename
            savePath = downloadPath + File.separator + fileName;
        } else {
            // It's a full file path - use as is
            savePath = downloadPath;
        }
    }
    
    System.out.println("Will save as: " + savePath);
    
    // Send download request
    String downloadRequest = Protocol.DOWNLOAD_REQUEST + Protocol.DELIMITER + 
                            owner + Protocol.DELIMITER + fileName;
    sendCommand(downloadRequest);
    
    // Get response
    String response = (String) in.readObject();
    String[] parts = response.split(Protocol.DELIMITER);
    
    if (parts[0].equals(Protocol.ERROR)) {
        System.out.println("Download failed: " + parts[1]);
        return;
    }
    
    if (!parts[0].equals(Protocol.DOWNLOAD_START)) {
        System.out.println("Unexpected response: " + response);
        return;
    }
    
    String downloadFileName = parts[1];
    long fileSize = Long.parseLong(parts[2]);
    
    System.out.println("Downloading: " + downloadFileName + " (" + fileSize + " bytes)");
    
    // Receive file chunks
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    int counter = 0;
    while (true) {
        String data = (String) in.readObject();
        
        if (data.startsWith(Protocol.DOWNLOAD_COMPLETE)) {
            break;
        }
        
        byte[] chunk = Base64.getDecoder().decode(data);
        baos.write(chunk);
        System.out.println("written chunk no. " + counter);
        counter++;
    }
    
    // Create parent directories if they don't exist
    File saveFile = new File(savePath);
    File parentDir = saveFile.getParentFile();
    if (parentDir != null && !parentDir.exists()) {
        parentDir.mkdirs();
    }
    
    // Save file
    byte[] fileData = baos.toByteArray();
    Files.write(Paths.get(savePath), fileData);
    
    System.out.println("File downloaded successfully: " + savePath + " (" + fileData.length + " bytes)");
}
    //make file request
    private void makeFileRequest() throws Exception {
        System.out.print("Enter file description: ");
        String description = scanner.nextLine().trim();
        
        System.out.print("Recipient (username or 'ALL' for broadcast): ");
        String recipient = scanner.nextLine().trim();
        
        String command = Protocol.MAKE_FILE_REQUEST + Protocol.DELIMITER + 
                        description + Protocol.DELIMITER + recipient;
        sendCommand(command);
        
        String response = recieveResponse();
        System.out.println("\n" + response);
    }
    private void viewMessages() throws Exception {
        sendCommand(Protocol.VIEW_MESSAGES);
        String response = recieveResponse();
        System.out.println("\n" + response);
    }
    private void viewHistory() throws Exception {
        sendCommand(Protocol.VIEW_HISTORY);
        String response = recieveResponse();
        System.out.println("\n" + response);
    }
    private void logout() throws Exception {
        sendCommand(Protocol.LOGOUT);
        
        
        if (socket != null && !socket.isClosed()) {
            socket.close();
        }
        System.out.println("\nLogged out successfully.");
    }





    ////////////////main method////////////////
    public static void main(String[] args) {
        Client client = new Client();
        String host = "localhost";
        int port = 6666;
        

        //command line arguments for host and port
        if (args.length >= 2) {
            host = args[0];
            port = Integer.parseInt(args[1]);
        }

        if (client.connect(host, port)) {
            client.run();
        } else {
            System.out.println("Failed to connect to server.");
        }
    }
}
