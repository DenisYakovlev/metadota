import StatusBar from "./StatusBar"
import PlayersTable from "./PlayersTable"
import Predictions from "./Predictions"

export default function Wrapper(){
    return (
        <>
            <StatusBar />
            <PlayersTable />
            <Predictions />
        </>
    )
}