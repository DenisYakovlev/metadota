import {useEffect, useState} from "react"
import {BrowserRouter , Routes, Route} from "react-router-dom"
import {UserContext} from "./contexts/UserContext"

import "./App.css"

import { MainLayout, AuthLayout, Home, Config, Dota, Csgo, SignIn, SignUp } from "./pages"


export default function App(){
    const [user, setUser] = useState(localStorage.getItem("auth_token"))
    
    return (
        <BrowserRouter>
            <UserContext.Provider value={{user, setUser}}>
                <Routes>
                    <Route path="/" element={<MainLayout />}>
                        <Route index element={<Home />}/>
                        <Route path="config" element={<Config />}/>
                        <Route path="dota" element={<Dota />} />
                        <Route path="csgo" element={<Csgo />} />
                        <Route path="auth" element={<AuthLayout />}>
                            <Route path="signin" element={<SignIn />} />
                            <Route path="signup" element={<SignUp />} />
                        </Route>
                    </Route>
                </Routes>
            </UserContext.Provider>
        </BrowserRouter>
    )
}

