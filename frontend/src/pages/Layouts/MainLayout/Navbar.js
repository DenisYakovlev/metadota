import { Link } from "react-router-dom"
import { useContext } from "react"
import logo from "../../../assets/logo.png"
import { UserContext } from "../../../contexts/UserContext"

import "./Navbar.css"

export default function Navbar(){
    const {user, setUser} = useContext(UserContext)
    
    const handleLogOut = () => {
        setUser(null)
        localStorage.removeItem("auth_token")
        localStorage.removeItem("gsi_token")
    }

    return(
        <nav className="navbar">
            <Link to="/"><img src={logo} alt="website logo" className="logo"/></Link>

            <div className="navbar-links">
                <Link to="dota">DOTA</Link>
                <Link to="csgo">CS:GO</Link>
                <Link to="config">CONFIG</Link>
            </div>

            <div className="navbar-auth">
            {user
                ? <span onClick={handleLogOut}>Log Out</span>
                : <Link to="auth/signin">Sign In</Link>}
            </div>
        </nav>
    )
}