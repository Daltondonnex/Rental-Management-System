import { useContext } from "react";
// import { AuthContext } from "../context/AuthContext";
import { createcontext } from "react";

const useAuth = () => {
    const AuthContext = createcontext();
    return useContext(AuthContext);
};

export default useAuth;