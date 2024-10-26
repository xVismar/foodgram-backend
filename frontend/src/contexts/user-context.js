import React, { createContext, useState, useEffect } from "react";

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  useEffect(() => {
    if (user) {
      localStorage.setItem("user", JSON.stringify(user));
    } else {
      localStorage.removeItem("user");
    }
  }, [user]);

  const setAvatar = (avatar) => {
    setUser((prevUser) => ({ ...prevUser, avatar }));
  };

  return (
    <UserContext.Provider value={{ user, setUser, setAvatar }}>
      {children}
    </UserContext.Provider>
  );
};

export default UserProvider;
export { UserContext };