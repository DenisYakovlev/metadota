import { useContext, useEffect, useState } from "react"
import { DotaContext } from "../../contexts/DotaContext"
import status_online from "../../assets/status_online.png"
import status_offline from "../../assets/status_offline.png"
import "./StatusBar.css"

export default function StatusBar(){
    const {lastMessage} = useContext(DotaContext)
    const [isGoing, setIsGoing] = useState("false")
    const [matchId, setMatchId] = useState("unknown")
    const [radiantWinChance, setRadiantWinChance] = useState("unknown")
    const [pickPower, setPickPower] = useState("unknown")

    useEffect(() => {
        let data = JSON.parse(lastMessage.data)
        setIsGoing(data.message.status.is_going)
        setMatchId(data.message.game.match_id)
        setRadiantWinChance(data.message.game.predictions.radiant_win_chance)
        setPickPower(data.message.game.counter)
    }, [lastMessage])

    return (
        <div className='dota-status'>
            <div className='dota-status-bar'>
                <span>
                    status: <img src={isGoing == true ? status_online : status_offline} className="dota-status-img" loading="lazy"/>
                </span>
                <span>
                    match id: {matchId ? matchId : "unkown"}
                </span>
            </div>
            <div className="dota-status-bar">
                <span>
                    radiant win chance: {radiantWinChance ? radiantWinChance : "unknown"}
                </span>
                <span>
                    pick power: {pickPower ? pickPower : "unknown"}
                </span>
            </div>
        </div>
    )
}