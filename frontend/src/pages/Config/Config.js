import { useContext } from "react"
import { UserContext } from "../../contexts/UserContext"
import { Link } from "react-router-dom"
import "./Config.css"
import cog from "../../assets/config_cog.png"

export default function Config(){
    const {user, setUser} = useContext(UserContext)

    const handleFileUpload = (url, filename) => {
        fetch(url, {
            method: "GET",
            headers: {
                "Authorization": `Token ${user}`
            }
        })
        .then( response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(new Blob([blob]));

            const link = document.createElement('a');
            link.href = url;
            link.download = `gamestate_integration_${filename}.cfg`;

            document.body.appendChild(link);

            link.click();

            link.parentNode.removeChild(link);
        })
        .catch(error => {
            alert("Coulnd't download file. User is not authorized")
        })
    }

    const handleDotaUpload = () =>{
        const url = "http://localhost:8000/config/gsi_dota"
        const filename = "dota"

        handleFileUpload(url, filename)
    }

    const handleCSGOUpload = () =>{
        const url = "http://localhost:8000/config/gsi_csgo"
        const filename = "csgo"

        handleFileUpload(url, filename)
    }

    return(
        <div className="config-page">
            <div className="config-layout">
                <div className="config-text">
                    <div className="text-unit">
                        <span className="config-header">Authorization:</span> 
                        {user 
                            ? <span>Your're successfully authorized</span> 
                            : <span>You need to be <Link to="../auth/signin">authorized</Link></span>}
                    </div>
                    <div className="text-unit">
                        <span className="config-header">GameState Integration:</span>
                        {user
                            ? <div className="config-buttons">
                                <button className="config-btn" onClick={handleDotaUpload}>Download Dota2 gsi</button>
                                <button className="config-btn" onClick={handleCSGOUpload}>Download CS:GO gsi</button>
                            </div>
                            : <span>You need to be <Link to="../auth/signin">authorized</Link></span>}
                    </div>
                    <div className="cofing-instruction">
                        <span className="config-header">Your final steps:</span>
                        <p>- Find Steam directory on your PC</p>
                        <p>- Dota path: Steam\steamapps\common\dota 2 beta\game\dota\cfg</p>
                        <p>- CS:GO path: Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg</p>
                        <p>- Place "gamestate_integration_metadota.cfg file in gamestate_integration folder</p>
                        <p>- Open your game and while spectating matches, you can see it in Dota section</p>
                    </div>
                </div>
                <img src={cog} alt="config cog" className="config-img"/>
            </div>
        </div>
    )
}