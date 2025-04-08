// src/pages/LoginSignup.js
import React, { useState } from "react";
import { Link } from "react-router-dom";

const LoginSignup = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6 text-center">
          Organizational Assistant
        </h1>
        <div className="flex justify-center mb-6">
          <button
            onClick={() => setIsLogin(true)}
            className={`px-4 py-2 ${isLogin ? "bg-blue-500 text-white" : "bg-gray-200"}`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`px-4 py-2 ${!isLogin ? "bg-blue-500 text-white" : "bg-gray-200"}`}
          >
            Signup
          </button>
        </div>
        {isLogin ? (
          <form>
            <input
              type="email"
              placeholder="Email"
              className="w-full p-2 mb-4 border rounded"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full p-2 mb-4 border rounded"
            />
            <button className="w-full bg-blue-500 text-white p-2 rounded">
              Login
            </button>
            <p className="text-center mt-4">
              <Link to="/forgot-password" className="text-blue-500">
                Forgot Password?
              </Link>
            </p>
          </form>
        ) : (
          <form>
            <input
              type="text"
              placeholder="Name"
              className="w-full p-2 mb-4 border rounded"
            />
            <input
              type="email"
              placeholder="Email"
              className="w-full p-2 mb-4 border rounded"
            />
            <input
              type="password"
              placeholder="Password"
              className="w-full p-2 mb-4 border rounded"
            />
            <button className="w-full bg-blue-500 text-white p-2 rounded">
              Signup
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginSignup;