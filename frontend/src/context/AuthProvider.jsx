import { useState } from "react";
import api from "../services/api";
import { AuthContext } from "./authContext";

export default function AuthProvider({ children }) {
    
    const [user, setUser] = useState(null);

    const login = async (username, password) => {
        try {
            const formData = new URLSearchParams();

            formData.append("username", username);
            formData.append("password", password);

            const response = await api.post("/login", formData, {
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            const token = response.data.access_token;

            localStorage.setItem("token", token);

            setUser({
                username,
            });

            return true;

        } catch (error) {
            console.error(error);
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                login,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}