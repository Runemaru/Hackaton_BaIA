import { percentage, formatDate } from "../utils/formatters";

import rainIcon from "../assets/rain.svg";
import droughtIcon from "../assets/drought.svg";
import fireIcon from "../assets/fire.svg";

function ForecastMetric({ icon, label, value }) {
  return (
    <article className="forecast-metric">
      <img src={icon} alt="" />

      <span>{label}</span>
      <strong>{percentage(value)}</strong>
    </article>
  );
}

export function TomorrowForecast({ forecast }) {
  return (
    <section className="tomorrow-section">
      <div className="section-title">
        <div>
          <small>Previsão para amanhã</small>
          <h2>{forecast?.date_label}</h2>
        </div>
      </div>
        <div className="tomorrow-grid">
          <ForecastMetric
            icon={rainIcon}
            label="Chuva"
            value={forecast?.rain?.percentage}
            level={forecast?.rain?.level}
          />

          <ForecastMetric
            icon={droughtIcon}
            label="Seca"
            value={forecast?.drought?.percentage}
            level={forecast?.drought?.level}
          />

          <ForecastMetric
            icon={fireIcon}
            label="Queima"
            value={forecast?.burning?.percentage}
            level={forecast?.burning?.level}
          />
        </div>
    </section>
  );
}
