
package models;

import java.io.Serializable;

//ChunkInfo stores temporary information during file upload
 
public class ChunkInfo implements Serializable {
    private String fileID;
    private int chunkSize;
    private int totalChunks;
    private int receivedChunks;
    private long totalSize;
    
    public ChunkInfo(String fileID, int chunkSize, long totalSize) {
        this.fileID = fileID;
        this.chunkSize = chunkSize;
        this.totalSize = totalSize;
        this.totalChunks = (int) Math.ceil((double) totalSize / chunkSize);
        System.out.println("DEBUGGGG ChunkInfo total chunks calculated: " + this.totalChunks);
        this.receivedChunks = 0;
    }
    
    public String getFileID() { return fileID; }
    public int getChunkSize() { return chunkSize; }
    public int getTotalChunks() { return totalChunks; }
    public int getReceivedChunks() { return receivedChunks; }
    public void incrementReceivedChunks() { receivedChunks++; }
    public long getTotalSize() { return totalSize; }
}