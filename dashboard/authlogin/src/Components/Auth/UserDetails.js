import { useEffect, useState } from "react";
import styles from "./Auth.module.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const UserDetails = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const fetchUserDetails = async (token) => {
    return await axios.get("http://localhost:3001/api/auth/getUserDetails", {
      withCredentials: true, // send cookie
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  };

  useEffect(() => {
    // Fetch user details from backend
    const fetchUser = async () => {
      const accessToken = localStorage.getItem("accessToken");
      if (!accessToken) {
        navigate("/login");
        return;
      }
      try {
        const res = await fetchUserDetails(accessToken);
        setUser(res.data);
      } catch (error) {
        const status = error.response.status;
        if (status == 401 || status == 403) {
          try {
            console.log("Access Token Expxired");
            const refreshRes = await axios.get(
              "http://localhost:3001/api/auth/refresh",
              {
                withCredentials: true,
              }
            );
            const newAccessToken = refreshRes.data.accessToken;
            localStorage.setItem("accessToken", newAccessToken);
            const retryRes = await fetchUserDetails(newAccessToken);
            setUser(retryRes.data);
          } catch (refresherror) {
            console.log("Refresh token expired");

            localStorage.clear();
            navigate("/login");
          }
        }
      }
    };

    fetchUser();
  }, [navigate]);

  const handleLogout = async () => {
    try {
      await axios.post(
        "http://localhost:3001/api/auth/logout",
        {},
        {
          withCredentials: true,
        }
      );
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      alert("Logout failed. Please try again.");
    }
  };

  if (!user) {
    return (
      <div className={styles.authContainer}>
        <div className={styles.authForm}>
          <h2 className={styles.authTitle}>Welcome to the Dashboard</h2>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.authContainer}>
      <div className={styles.authForm}>
        <h2 className={styles.authTitle}>Welcome to the Dashboard</h2>
      </div>
    </div>
  );
};

export default UserDetails;
