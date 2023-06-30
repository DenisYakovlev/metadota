import MainInfo from "./MainInfo"
import StartInfo from "./StartInfo"

export default function Home(){
    return(
        <div className="home-wrapper">
            <MainInfo />
            <StartInfo />
        </div>
    )
}