import logo from "../assets/logo-radar.svg";


export function Header({ connected, lastUpdate }) {
  return (
    <header className="top-header">
      <div className="brand">
        <img src={logo} alt="Radar Climático" />

        <div>
          <h1>Radar <span>Climático</span></h1>
          <p>Previsão ambiental em tempo real</p>
        </div>
      </div>

      <div className="header-info">
        <div className={connected ? "connection online" : "connection offline"}>
          {connected ? "Conectado" : "Desconectado"}
        </div>

        <div>
          <small>Última atualização</small>
          <strong>{lastUpdate || "Aguardando dados..."}</strong>
        </div>
      </div>
    </header>
  );
}
