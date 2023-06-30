import { useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { DotaContext } from '../../contexts/DotaContext';

import Wrapper from './Wrapper';

import "./Dota.css"

export default function Dota(){
    const { sendMessage, lastMessage, readyState } = useWebSocket(`ws://localhost:8000/ws/gsi/${localStorage.getItem("gsi_token")}`);
    const [loaded, setLoaded] = useState(false)

    useEffect(() => {
        try{
            let data = JSON.parse(lastMessage.data)
            if(data.message.status.is_going == true && data.message.provider == "dota"){
                setLoaded(true)
            }
            else{
                setLoaded(false)
            }
        }
        catch(e){
            console.log("Waiting for message")
        }
    }, [lastMessage])

    return (
        <DotaContext.Provider value={{lastMessage}}>
            <div className='dota-layout'>
                <div className='dota-window'>
                    {lastMessage && loaded == true
                        ? <Wrapper />
                        : <span className="dota-error">Waiting for connection</span>
                    }
                </div>
            </div>
        </DotaContext.Provider>
    )
}