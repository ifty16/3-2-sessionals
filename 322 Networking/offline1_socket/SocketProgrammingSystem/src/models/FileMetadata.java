
package models;

import java.io.Serializable;
import java.util.Date;


// //FileMetadata stores information about uploaded files

public class FileMetadata implements Serializable {
    private String fileName;
    private long fileSize;
    private String owner;
    private String accessType; // PRIVATE or PUBLIC
    private String fileID;
    private String requestID; // null if not uploaded in response to request
    private Date uploadDate;
    
    public FileMetadata(String fileName, long fileSize, String owner, String accessType) {
        this.fileName = fileName;
        this.fileSize = fileSize;
        this.owner = owner;
        this.accessType = accessType;
        this.uploadDate = new Date();
    }

    
    // Getters and Setters
    public String getFileName() { return fileName; }
    public long getFileSize() { return fileSize; }
    public String getOwner() { return owner; }
    public String getAccessType() { return accessType; }
    public String getFileID() { return fileID; }
    public void setFileID(String fileID) { this.fileID = fileID; }
    public String getRequestID() { return requestID; }
    public void setRequestID(String requestID) { this.requestID = requestID; }
    public Date getUploadDate() { return uploadDate; }
    public void setAccessType(String accessType) { this.accessType = accessType; }
}








