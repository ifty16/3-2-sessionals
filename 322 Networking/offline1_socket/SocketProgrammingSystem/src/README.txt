javac -d bin src/utils/*.java src/models/*.java src/server/*.java src/client/*.java

java -cp bin server.server

java -cp bin client.Client