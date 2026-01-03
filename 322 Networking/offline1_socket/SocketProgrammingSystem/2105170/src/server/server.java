package server;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.file.Files;
import java.nio.file.Paths;

public class server {
    public static void main(String[] args) {
        ////////////////create server data directory if not exist
        try {
            Files.createDirectories(Paths.get(ServerConfig.SERVER_DATA_DIR));
            System.out.println("Server data directory ready: " + ServerConfig.SERVER_DATA_DIR);
        } catch (Exception e) {
            System.err.println("Failed to create server data directory: " + e.getMessage());
            return;
        }

        // Print server configuration
        System.out.println("-----FILE SERVER STARTED------");
        System.out.println("Port: " + ServerConfig.SERVER_PORT);
        System.out.println("Max Buffer Size: " + (ServerConfig.MAX_BUFFER_SIZE / (1024 * 1024)) + " MB");
        System.out.println("Min Chunk Size: " + (ServerConfig.MIN_CHUNK_SIZE / 1024) + " KB");
        System.out.println("Max Chunk Size: " + (ServerConfig.MAX_CHUNK_SIZE / 1024) + " KB");
        System.out.println("===========================");


        //initially history restore korbe


        // Load existing users from directory
        System.out.println("\nLoading existing users...");
        ServerConfig.loadExistingUsers();
        // Load existing files from activity logs
        System.out.println("Loading existing files...");
        ServerConfig.loadExistingFiles();
        // Load message history
        System.out.println("Loading message history...");
        ServerConfig.loadMessagesFromFile();
    
 
        

        //crearte server socket
        try(ServerSocket welcomeSocket = new ServerSocket(ServerConfig.SERVER_PORT)) { //6666
            System.out.println("Server is listening on port " + ServerConfig.SERVER_PORT + "...");

            while (true) {
                try {
                    // Wait for client connection
                    System.out.println("Waiting for connection...");
                    Socket socket = welcomeSocket.accept(); // ekhane block kore thakbe joto khon na kono client connect korche
                    System.out.println("Connection established from: " + socket.getInetAddress().getHostAddress()); // client er IP ta dekhabe
                    
                    // Create and start client handler thread
                    ClientHandler handler = new ClientHandler(socket);
                    handler.start(); // new thread e client handle korbe
                    
                } catch (IOException e) {
                    System.err.println("Error accepting client connection: " + e.getMessage());
                }
            }
        } catch (Exception e) {
            System.err.println("Server error: " + e.getMessage());
        }
    }
}
