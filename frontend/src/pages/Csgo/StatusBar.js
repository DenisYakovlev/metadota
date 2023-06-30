import { useContext, useEffect, useState } from "react";
import { CSGOContext } from "../../contexts/CSGOContext";
import status_online from "../../assets/status_online.png"
import status_offline from "../../assets/status_offline.png"
import "./StatusBar.css"

export default function StatusBar(){
    const {lastMessage} = useContext(CSGOContext)
    const [isGoing, setIsGoing] = useState("false")
    const [map, setMap] = useState("")

    useEffect(() => {
        let data = JSON.parse(lastMessage.data)
        setIsGoing(data.message.status.is_going)
        setMap(data.message.game.map)
    }, [lastMessage])

    return (
        <div className='csgo-status'>
            <div className='csgo-status-bar'>
                <span>
                    status: <img src={isGoing == true ? status_online : status_offline} className="csgo-status-img" loading="lazy"/>
                </span>
                <span>
                    map: {map ? map : "unkown"}
                </span>
            </div>
        </div>
    )
}