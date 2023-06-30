import { useContext, useState } from "react"
import { UserContext } from "../../contexts/UserContext"
import { Link } from "react-router-dom"
import ErrorPage from "./ErrorPage"
import "./Auth.css"

export default function SignUp(){
    const {user, setUser} = useContext(UserContext)
    const [username, setUsername] = useState("")
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [status, setStatus] = useState("")

    const handleSubmit = e => {
        e.preventDefault()

        fetch("http://localhost:8000/auth/signup", {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirmPassword
            })
        })
        .then( response => {
            if(response.ok){
                return response.json()
            }
            else{
                throw Error("auth error")
            }
        })
        .then( data => {
            localStorage.setItem("auth_token", data["auth_token"])
            localStorage.setItem("gsi_token", data["gsi_token"])
            setUser(localStorage.getItem("auth_token"))
        })
        .catch( error =>{
            setStatus("Wrong credentials")
            setPassword("")
            setConfirmPassword("")
        })
    }

    const handleChangeUsername = e => {
        e.preventDefault()
        setUsername(e.target.value)
    }

    const handleChangeEmail = e => {
        e.preventDefault()
        setEmail(e.target.value)
    }

    return (
        <>
            {user ? 
                <ErrorPage /> :
                <form className="auth-form">
                <div className="form-header">
                    Registration
                </div>
                <div className="form-input">
                    <label for="username_input">username</label>
                    <input
                        name="username_input"
                        type="text"
                        value={username}
                        onChange={handleChangeUsername}
                    />
                </div>
                <div className="form-input">
                    <label for="email_input">email</label>
                    <input
                        name="email_input"
                        type="text"
                        value={email}
                        onChange={handleChangeEmail}
                    />
                </div>
                <div className="form-input">
                    <label for="password">password</label>
                    <input
                        name="password"
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)} 
                    />
                </div>
                <div className="form-input">
                    <label for="confirm password">confirm password</label>
                    <input
                        name="confirm password"
                        type="password"
                        value={confirmPassword}
                        onChange={e => setConfirmPassword(e.target.value)} 
                    />
                </div>
                <div className="error-status">{status}</div>
                <button onClick={handleSubmit} className="submit-btn">submit</button>
                <div className="form-link">or <Link to="../signin">Sign In</Link></div>
            </form>
            }
        </>
    )
}