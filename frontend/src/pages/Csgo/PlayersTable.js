import { useContext, useState, useEffect } from "react"
import { CSGOContext } from "../../contexts/CSGOContext"
import "./PlayersTable.css"

export default function StatusBar(){
    const {lastMessage} = useContext(CSGOContext)
    const [round, setRound] = useState("unknown")
    const [tPlayers, setTPlayers] = useState([])
    const [ctPlayers, setCTPlayers] = useState([])


    useEffect(() => {
        let data = JSON.parse(lastMessage.data)
        const players = data.message.game.players
        setRound(data.message.game.round)
        setTPlayers(players[0].filter(player => player["team"] == "T"))
        setCTPlayers(players[0].filter(player => player["team"] == "CT"))

    }, [lastMessage])

    return (
        <div className="csgo-table">
            <span className="csgo-timer">Round: {round ? round : "unknown"}</span>
            <span className="csgo-table-delimiter">Terrorists</span>
            <table>
                <tr>
                    <th>Player</th>
                    <th>Health</th>
                    <th>Armor</th>
                    <th>Money</th>
                    <th>Kills</th>
                    <th>Assists</th>
                    <th>Deaths</th>
                    <th>MVPS</th>
                    <th>Score</th>
                    <th>Weapons</th>
                </tr>
                {tPlayers.map( (player, idx) => {
                    return (
                        <tr id={idx}>
                            <th>{player.name}</th>
                            <th>{player.state.health}</th>
                            <th>{player.state.armor}</th>
                            <th>{player.state.money}</th>
                            <th>{player.stats.kills}</th>
                            <th>{player.stats.assists}</th>
                            <th>{player.stats.deaths}</th>
                            <th>{player.stats.mvps}</th>
                            <th>{player.stats.score}</th>
                            <th className="csgo-weapons">
                                {player.weapons.map( (item, idx) => {
                                    return (
                                        <>
                                            {item.name == "empty"
                                                ? <span></span>
                                                : <img src={item.url} alt={item.name} className="csgo-table-item-img" loading="lazy"/>}
                                        </>
                                    )
                                })}
                            </th>
                        </tr>
                    )
                })}
                <span className="csgo-table-delimiter">Counter-Terrorists</span>
                {ctPlayers.map( (player, idx) => {
                    return (
                        <tr id={idx}>
                            <th>{player.name}</th>
                            <th>{player.state.health}</th>
                            <th>{player.state.armor}</th>
                            <th>{player.state.money}</th>
                            <th>{player.stats.kills}</th>
                            <th>{player.stats.assists}</th>
                            <th>{player.stats.deaths}</th>
                            <th>{player.stats.mvps}</th>
                            <th>{player.stats.score}</th>
                            <th className="csgo-weapons">
                                {player.weapons.map( (item, idx) => {
                                    return (
                                        <>
                                            {item.name == "empty"
                                                ? <span></span>
                                                : <img src={item.url} alt={item.name} className="csgo-table-item-img" loading="lazy"/>}
                                        </>
                                    )
                                })}
                            </th>
                        </tr>
                    )
                })}
            </table>
        </div>
    )
}