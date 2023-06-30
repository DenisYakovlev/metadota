import credentials from "../../../assets/credentials.png"
import "./Footer.css"

export default function Footer(){
    return (
        <footer>
            <hr />
            <img src={credentials} alt="credential links"/>
            <span>2023</span>
        </footer>
    )
}