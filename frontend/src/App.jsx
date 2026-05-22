import { useEffect, useMemo, useState } from "react";

import { createPredictionSocket } from "./services/websocket";
import { formatDate } from "./utils/formatters";

import { Header } from "./components/Header";
import { RegionFilter } from "./components/RegionFilter";
import { TomorrowForecast } from "./components/TomorrowForecast";
import { WeekForecast } from "./components/WeekForecast";

import "./styles.css";

function App() {
  const [connected, setConnected] = useState(false);
  const [predictions, setPredictions] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState("Salvador - BA");

  useEffect(() => {
    const socket = createPredictionSocket({
      onOpen: () => setConnected(true),
      onClose: () => setConnected(false),
      onMessage: (data) => {
        setPredictions((prev) => [data, ...prev].slice(0, 50));
      },
    });

    return () => socket.close();
  }, []);

  const regions = useMemo(() => {
    return [...new Set(predictions.map((item) => item.region))];
  }, [predictions]);

  const filteredPredictions = useMemo(() => {
  return predictions.filter((item) => item.region === selectedRegion);
  }, [predictions, selectedRegion]);

  const currentPrediction = filteredPredictions[0];

  return (
    <div className="app">
      <Header
        connected={connected}
        lastUpdate={currentPrediction?.generated_at_label || null}
      />

      <main className="dashboard">
        <RegionFilter
          selectedRegion={selectedRegion}
          onChange={setSelectedRegion}
        />

        {!currentPrediction ? (
          <section className="empty-state">
            <h2>Aguardando dados do WebSocket...</h2>
            <p>Quando o modelo publicar uma previsão, ela será exibida aqui.</p>
          </section>
        ) : (
          <>
            <TomorrowForecast forecast={currentPrediction.tomorrow} />

            <WeekForecast forecast={currentPrediction.week_forecast} />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
