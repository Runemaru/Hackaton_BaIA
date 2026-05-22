import { percentage, formatDate } from "../utils/formatters";

import rainIcon from "../assets/rain.svg";
import droughtIcon from "../assets/drought.svg";
import fireIcon from "../assets/fire.svg";

export function WeekForecast({ forecast = [] }) {
  return (
    <section className="week-section">
      <div className="section-title">
        <div>
          <small>Previsão para a semana</small>
          <h2>Próximos dias</h2>
        </div>
      </div>

      <div className="week-grid">
        {forecast.map((day) => (
          <article className="day-card" key={day.date}>
            <strong className="day-date">{formatDate(day.date)}</strong>

            <div className="day-metric">
              <img src={rainIcon} alt="" />
              <span>Chuva</span>
              <strong>{percentage(day.rain.percentage)}</strong>
            </div>

            <div className="day-metric">
              <img src={droughtIcon} alt="" />
              <span>Seca</span>
              <strong>{percentage(day.drought.percentage)}</strong>
            </div>

            <div className="day-metric">
              <img src={fireIcon} alt="" />
              <span>Queima</span>
              <strong>{percentage(day.burning.percentage)}</strong>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
