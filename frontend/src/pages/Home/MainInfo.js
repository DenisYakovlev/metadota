import { Link } from "react-router-dom"
import dotaLogo from "../../assets/dota_logo.png"
import csgoLogo from "../../assets/csgo_logo.png"
import "./MainInfo.css"


export default function MainInfo(){
    return (
        <div className="home-info">
            <div className="info-text">
                <span>ANALYZE YOUR GAMES IN REAL-TIME</span>
                <span>WITH AI</span>
            </div>
            <div className="info-imgs">
                <Link to="dota"><img src={dotaLogo} alt="dota logo"/></Link>
                <Link to="csgo"><img src={csgoLogo} alt="csgo logo"/></Link>
            </div>
        </div>
    )
}