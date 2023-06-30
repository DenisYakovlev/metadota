import { useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { CSGOContext } from '../../contexts/CSGOContext';

import Wrapper from './Wrapper';

import "./Csgo.css"

export default function Csgo(){
    const {lastMessage} = useWebSocket(`ws://localhost:8000/ws/gsi/${localStorage.getItem("gsi_token")}`);
    const [loaded, setLoaded] = useState(false)

    useEffect(() => {
        try{
            let data = JSON.parse(lastMessage.data)
            if(data.message.status.is_going == true && data.message.provider == "csgo"){
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
        <CSGOContext.Provider value={{lastMessage}}>
            <div className='csgo-layout'>
                <div className='csgo-window'>
                    {lastMessage && loaded == true
                        ? <Wrapper />
                        : <span className="csgo-error">Waiting for connection</span>
                    }
                </div>
            </div>
        </CSGOContext.Provider>
    )
}