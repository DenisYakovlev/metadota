import { useContext, useEffect, useState } from "react"
import { DotaContext } from "../../contexts/DotaContext"

import "./PlayersTable.css"

export default function PlayersTable(){
    const {lastMessage} = useContext(DotaContext)
    const [gameTime, setGameTime] = useState("unknown")
    const [radiantHeroes, setRadiantHeroes] = useState([])
    const [radiantStats, setRadiantStats] = useState([])
    const [radiantItems, setRadiantItems] = useState([])
    const [direHeroes, setDireHeroes] = useState([])
    const [direStats, setDireStats] = useState([])
    const [direItems, setDireItems] = useState([])

    
    useEffect(() => {
        let data = JSON.parse(lastMessage.data)
        setGameTime(data.message.game.game_time)
        setRadiantHeroes(data.message.game.radiant_heroes.heroes)
        setRadiantStats(data.message.game.radiant_heroes.stats)
        setRadiantItems(data.message.game.radiant_items)
        setDireHeroes(data.message.game.dire_heroes.heroes)
        setDireStats(data.message.game.dire_heroes.stats)
        setDireItems(data.message.game.dire_items)
    }, [lastMessage])
    
    return (
        <div className="dota-table">
            <span className="dota-timer">Time: {gameTime ? gameTime : "unknown"}</span>
            <table>
                <tr>
                    <th>Player</th>
                    <th>Kills</th>
                    <th>Deaths</th>
                    <th>Assists</th>
                    <th>Net worth</th>
                    <th>XPM</th>
                    <th>Items</th>
                </tr>
                {radiantHeroes.map( (hero, idx) => {
                    return (
                        <tr id={idx}>
                            <th><img src={hero.img} alt={hero.name} className="dota-table-img" loading="lazy"/></th>
                            <th>{radiantStats[idx][0]}</th>
                            <th>{radiantStats[idx][1]}</th>
                            <th>{radiantStats[idx][2]}</th>
                            <th>{radiantStats[idx][3]}</th>
                            <th>{radiantStats[idx][4]}</th>
                            <th>
                                {radiantItems[`player_${idx}`].map( (item, idx) => {
                                    return (
                                        <>
                                            {item.name == "empty"
                                                ? <span></span>
                                                : <img src={item.img} alt={item.name} className="dota-table-item-img" loading="lazy"/>}
                                        </>
                                    )
                                })}
                            </th>
                        </tr>
                    )
                })}
                <span className="dota-table-delimiter">Dire heroes</span>
                {direHeroes.map( (hero, idx) => {
                    return (
                        <tr id={idx}>
                            <th><img src={hero.img} alt={hero.name} className="dota-table-img" loading="lazy"/></th>
                            <th>{direStats[idx][0]}</th>
                            <th>{direStats[idx][1]}</th>
                            <th>{direStats[idx][2]}</th>
                            <th>{direStats[idx][3]}</th>
                            <th>{direStats[idx][4]}</th>
                            <th>
                                {direItems[`player_${idx}`].map( (item, idx) => {
                                    return (
                                        <>
                                            {item.name == "empty"
                                                ? <span></span>
                                                : <img src={item.img} alt={item.name} className="dota-table-item-img" loading="lazy"/>}
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