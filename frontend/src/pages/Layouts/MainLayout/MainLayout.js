import { Outlet } from "react-router-dom"
import Navbar from "./Navbar"
import Footer from "./Footer"

import "./MainLayout.css"


export default function MainLayout(){
    return (
        <div className="main-layout">
            <Navbar />
            <div className="main-outlet">
                <Outlet />
                <Footer />
            </div>
        </div>
    )
}