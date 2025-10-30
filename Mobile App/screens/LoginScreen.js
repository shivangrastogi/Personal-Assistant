import React, { useState } from "react";
import { View, TextInput, Button, Alert } from "react-native";

export default function LoginScreen({ navigation }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();

      if (data.success) {
        await fetch("http://127.0.0.1:5000/start-jarvis", { method: "POST" });
        navigation.navigate("Chat");
      } else {
        Alert.alert("Login Failed", data.message);
      }
    } catch (err) {
      console.log(err);
      Alert.alert("Error", "Could not connect to backend");
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput placeholder="Email" value={email} onChangeText={setEmail} />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}
