import { useContext, useEffect, useState } from "react"
import { DotaContext } from "../../contexts/DotaContext"
import "./Predictions.css"


export default function Predictions(){
    const {lastMessage} = useContext(DotaContext)
    const [predictions, setPredictions] = useState([])

    useEffect(() => {
        let data = JSON.parse(lastMessage.data)
        setPredictions(data.message.game.predictions)
    }, [lastMessage])

    return (
        <div className="dota-pred-table">
            <div className="dota-pred-item">
                <div className="dota-pred-header">Early Game</div>
                <div className="dota-pred-value">{predictions.early_game}</div>
            </div>
            <div className="dota-pred-item">
                <div className="dota-pred-header">Mid Game</div>
                <div className="dota-pred-value">{predictions.mid_game}</div>
            </div>
            <div className="dota-pred-item">
                <div className="dota-pred-header">Late Game</div>
                <div className="dota-pred-value">{predictions.late_game}</div>
            </div>
            <div className="dota-pred-item">
                <div className="dota-pred-header">Superlate Game</div>
                <div className="dota-pred-value">{predictions.superlate_game}</div>
            </div>
        </div>
    )
}