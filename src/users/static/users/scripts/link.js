$(() => {
    const nullOption = "<option disabled selected></option>";

    const $associations = $("#associations");
    const $districts = $("#districts");
    const $seasons = $("#seasons");
    const $leagues = $("#leagues");
    const $teams = $("#teams");

    let districtId = null;

    if (clear === true) {
        clearAssociations();

        $.get("/api/associations/", (response) => {
            response.associations.sort((a, b) => a.name.localeCompare(b.name)).forEach((association) => {
                $associations.append(`<option value="${association.bhvId}">${association.name} (${association.abbreviation})</option>`);
            });
        });
    }

    $associations.change((e) => {
        const associationId = e.target.value;
        clearDistricts();
        $.get(`/api/associations/${associationId}/districts/`, (response) => {
            response.districts.sort((a, b) => a.name.localeCompare(b.name)).forEach((district) => {
                $districts.append(`<option value="${district.bhvId}">${district.name}</option>`);
            });
        });
    });

    $districts.change((e) => {
        districtId = e.target.value;
        clearSeasons();
        $.get("/api/seasons/", (response) => {
            response.seasons.sort((a, b) => a.startYear - b.startYear).forEach((season) => {
                $seasons.append(`<option value="${season.startYear}">${season.startYear}/${season.startYear + 1}</option>`);
            });
        });
    });

    $seasons.change((e) => {
        const seasonStartYear = e.target.value;
        clearLeagues();
        $.get(`/api/districts/${districtId}/seasons/${seasonStartYear}/leagues/`, (response) => {
            response.leagues.sort((a, b) => a.name.localeCompare(b.name)).forEach((league) => {
                $leagues.append(`<option value="${league.bhvId}">${league.name}</option>`);
            });
        });
    });

    $leagues.change((e) => {
        const leagueId = e.target.value;
        clearTeams();
        $.get(`/api/leagues/${leagueId}/teams/`, (response) => {
            response.teams.sort((a, b) => a.name.localeCompare(b.name)).forEach((team) => {
                $teams.append(`<option value="${team.bhvId}">${team.name}</option>`);
            });
        });
    });

    function clearSelect($select) {
        $select.empty();
        $select.append(nullOption);
    }

    function clearAssociations() {
        clearSelect($associations);
        clearDistricts();
    }

    function clearDistricts() {
        clearSelect($districts);
        clearSeasons();
    }

    function clearSeasons() {
        clearSelect($seasons);
        clearLeagues();
    }

    function clearLeagues() {
        clearSelect($leagues);
        clearTeams();
    }

    function clearTeams() {
        clearSelect($teams);
    }

});
