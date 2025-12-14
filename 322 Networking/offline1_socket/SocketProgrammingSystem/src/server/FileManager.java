package server;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import models.FileMetadata;

public class FileManager {
    
    public static boolean createUserDirectory(String username){
        try {
            Path dirPath = Paths.get(ServerConfig.SERVER_DATA_DIR, username);
            if(!Files.exists(dirPath)){
                Files.createDirectories(dirPath);
                System.out.println("Created directory for user: " + username);
            }
            return true;
        } catch (Exception e) {
            System.out.println("Error creating directory for user: " + username+ ". " + e.getMessage());
            return false;
        }
    }

     //Logs upload/download activity to user's log file
     
    public static void logActivity(String username, String fileName, String action, String status, String accessType) {
    try {
        String logPath = ServerConfig.SERVER_DATA_DIR + username + "/activity_log.txt";
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        String timestamp = sdf.format(new Date());
        
        String logEntry = String.format("[%s] File: %s | Action: %s | Status: %s | Access: %s%n", timestamp, fileName, action, status, accessType);
        
        // Append to log file
        try (FileWriter fw = new FileWriter(logPath, true);
             BufferedWriter bw = new BufferedWriter(fw)) {
            bw.write(logEntry);
        }
    } catch (IOException e) {
        System.err.println("Error writing to log file: " + e.getMessage());
    }
}

    // Saves uploaded file chunks to disk
    public static boolean saveFile(String username, FileMetadata metadata, List<byte[]> chunks) {
        try {
            String filePath = ServerConfig.SERVER_DATA_DIR + username + "/" + metadata.getFileName();
            
            // Write all chunks to file
            try (FileOutputStream fos = new FileOutputStream(filePath)) {
                for (byte[] chunk : chunks) {
                    fos.write(chunk);
                }
            }
            
            System.out.println("File saved successfully: " + filePath);
            return true;
        } catch (IOException e) {
            System.err.println("Error saving file: " + e.getMessage());
            return false;
        }
    }

     
    //Reads a file from disk for download
     
    public static byte[] readFile(String username, String fileName) {
        try {
            String filePath = ServerConfig.SERVER_DATA_DIR + username + "/" + fileName;
            return Files.readAllBytes(Paths.get(filePath));
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return null;
        }
    }

    
     //Reads the activity log for a user
     
    public static String readActivityLog(String username) {
        try {
            String logPath = ServerConfig.SERVER_DATA_DIR + username + "/activity_log.txt";
            File logFile = new File(logPath);
            
            if (!logFile.exists()) {
                return "No activity log found.";
            }
            
            StringBuilder content = new StringBuilder();
            try (BufferedReader br = new BufferedReader(new FileReader(logFile))) {
                String line;
                while ((line = br.readLine()) != null) {
                    content.append(line).append("\n");
                }
            }
            
            return content.toString();
        } catch (IOException e) {
            return "Error reading log file: " + e.getMessage();
        }
    }
}
