import { Link } from "react-router-dom"

import userLogo from "../../assets/user_logo.png"
import configLogo from "../../assets/config_logo.jpg"
import "./StartInfo.css"

export default function StartInfo(){
    return (
        <div className="home-start">
            <div className="start-text">
                <span className="text-header">START RIGHT NOW</span>
                <span>sign up</span>
                <span>install config</span>
                <span>open your game</span>
            </div>
            <li className="start-links">
                <Link to="auth/signup">
                    <ul className="link-item">
                        <img src={userLogo} alt="auth img"/>
                        <span>Sign Up</span>
                    </ul>
                </Link>
                <Link to="config">
                    <ul className="link-item">
                        <img src={configLogo} alt="config img"/>
                        <span>Set up</span>
                    </ul>
                </Link>
            </li>
        </div>
    )
}