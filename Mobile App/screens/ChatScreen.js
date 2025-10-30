import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";

export default function ChatScreen() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchLogs = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/get-logs");
      const data = await res.json();
      setLogs(data.logs);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.chatContainer}>
        {logs.map((msg, index) => (
          <View
            key={index}
            style={[
              styles.message,
              msg.sender === "User" ? styles.userMsg : styles.jarvisMsg,
            ]}
          >
            <Text style={styles.msgText}>{msg.text}</Text>
          </View>
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#0a0a0a",
    padding: 10,
  },
  chatContainer: {
    paddingBottom: 20,
  },
  message: {
    maxWidth: "75%",
    padding: 10,
    borderRadius: 10,
    marginVertical: 5,
  },
  userMsg: {
    backgroundColor: "#005CFF",
    alignSelf: "flex-end",
  },
  jarvisMsg: {
    backgroundColor: "#262626",
    alignSelf: "flex-start",
  },
  msgText: {
    color: "#fff",
    fontSize: 16,
  },
});
