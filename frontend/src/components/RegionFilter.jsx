const AVAILABLE_REGIONS = [
  { name: "Salvador - BA", locked: false },
  { name: "Feira de Santana - BA", locked: true },
  { name: "Juazeiro - BA", locked: true },
  { name: "Barreiras - BA", locked: true },
  { name: "Vitória da Conquista - BA", locked: true },
];

export function RegionFilter({ selectedRegion, onChange }) {
  function handleChange(event) {
    const selected = AVAILABLE_REGIONS.find(
      (region) => region.name === event.target.value
    );

    if (selected?.locked) return;

    onChange(event.target.value);
  }

  return (
    <section className="region-filter">
      <label>Região</label>

      <select value={selectedRegion} onChange={handleChange}>
        {AVAILABLE_REGIONS.map((region) => (
          <option
            key={region.name}
            value={region.name}
            disabled={region.locked}
          >
            {region.locked ? `${region.name}` : region.name}
          </option>
        ))}
      </select>
    </section>
  );
}
