class FootballDashboardCard extends HTMLElement {
  set hass(hass) {
    if (!this.content) {
      const card = document.createElement('ha-card');
      this.content = document.createElement('div');
      card.appendChild(this.content);
      this.appendChild(card);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];

    if (!state) {
      this.content.innerHTML = 'Entity not found';
      return;
    }

    const fixtures = state.attributes.fixtures || [];
    const league = this.config.league || 'La Liga';

    this.content.innerHTML = `
      <div>
        <select id="league-select">
          <option value="140" ${league === 'La Liga' ? 'selected' : ''}>La Liga</option>
          <option value="39" ${league === 'Premier League' ? 'selected' : ''}>Premier League</option>
          <!-- Add more leagues here -->
        </select>
        <ul>
          ${fixtures.map(fixture => `
            <li>
              <img src="${fixture.home_team_logo}" alt="${fixture.home_team}" width="20">
              ${fixture.home_team} vs ${fixture.away_team}
              <img src="${fixture.away_team_logo}" alt="${fixture.away_team}" width="20">
              <br>Date: ${new Date(fixture.date).toLocaleString()}
              <br>Status: ${fixture.status}
            </li>
          `).join('')}
        </ul>
      </div>
    `;

    this.content.querySelector('#league-select').addEventListener('change', (e) => {
      this._setLeague(e.target.value);
    });
  }

  _setLeague(leagueId) {
    // Call the Home Assistant service to set the league
    this.hass.callService('football_dashboard', 'set_league', {
      league_id: leagueId
    });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }
}

customElements.define('football-dashboard-card', FootballDashboardCard);
