import { Link } from "react-router-dom"

export default function ErrorPage(){
    return (
        <div className="auth-form">
            <div className="form-header">
                Authorized successfully 
            </div>
            <div className="form-link">
                go back to <Link to="../../">Home page</Link>
            </div>
        </div>
    )
}