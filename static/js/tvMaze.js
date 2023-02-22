"use strict";

const $showsList = $("#shows-list");
const $episodesArea = $("#episodes-area");
const $episodesList = $("#episodes-list");
const $episodesTitle = $("#episodes-title");
const $searchForm = $("#search-form");
const $searchFormDiv = $("#search-form-div");
const $episodeListBack = $("#episodes-list-back");
const $castList = $("#cast-list");



// http://api.tvmaze.com/search/shows?q=friends
// http://api.tvmaze.com/shows/431/episodes //431 = friends Id
// http://api.tvmaze.com/shows/431/images // 431 = friends Id
 
const apiURL = 'http://api.tvmaze.com/';

 
/** Given a search term, search for tv shows that match that query.
 *
 *  Returns (promise) array of show objects: [show, show, ...].
 *    Each show object should contain exactly: {id, name, summary, image}
 *    (if no image URL given by API, put in a default image URL)
 */

async function getShowsByTerm(searchTerm) {
  // ADD: Remove placeholder & make request to TVMaze search shows API.
  const shows = await axios.get(`${apiURL}search/shows?q=${searchTerm}`)
  return shows.data
}

async function getShowsById(searchTerm) {
  // ADD: Remove placeholder & make request to TVMaze search shows API.
  const shows = await axios.get(`${apiURL}shows/${searchTerm}`)
  return shows.data
}

/** Given a show ID, get from API and return (promise) array of episodes:
 *      { id, name, season, number }
 */
async function getEpisodesOfShow(id) { 
  const episodes = await axios.get(`${apiURL}shows/${id}/episodes`);
  return episodes.data
}

async function getShowsCast(searchTerm) {
  // ADD: Remove placeholder & make request to TVMaze search shows API.
  const shows = await axios.get(`${apiURL}shows/${searchTerm}/cast`)
  return shows.data
}

async function getActorCast(actor_id) {
  const shows = await axios.get(`${apiURL}people/${actor_id}/castcredits`)
  return shows.data
}


/** Given list of shows, create markup for each and to DOM */



function populateShows(shows) {
  $showsList.empty();

  const regularBtn_html = `<button class="btn btn-info Show-getEpisodes mx-1">Episodes</button>`
  const loggedInBtn_html = show_id => `<a class="btn btn-success mx-1" id="LoggedIn-getEpisodes" href="/tvbuddy/shows/${show_id}">Episodes</a>`

  for (let item of shows) {
    let image;
    if (!item.show.image) {
      image = "/static/img/tvMissing.png"
    } else {
      image = item.show.image.original;
    }
    const $show = $(
      `<div class="Show col-md-12 col-lg-4 mb-4">
        <div class="card" style=" height: 40rem;">
          <img 
            src="${image}"
            alt="${item.show.name}" 
            class="mr-3 img-thumbnail show-data-img">
          <div class="card-body d-flex flex-column align-items-center justify-content-between">
            <h5 class="card-title">${item.show.name}</h5>
            <p class="card-text">${item.show.summary ? item.show.summary.substring(0, 300).concat("...") : "" }</p>
            <div class="w-25 d-flex" data-show-id="${item.show.id}" data-show-name="${item.show.name}">
              ${
                isUserLoggedIn() ?
                loggedInBtn_html(item.show.id) :
                regularBtn_html
              }
            </div>
          </div>
        </div>  
      </div>
    `);

    $showsList.append($show);  
  } 
}

function isUserLoggedIn() {
  // Checks the cookie for the user_login token
  return document.cookie.includes("user_login");
}


/** Handle search form submission: get shows from API and display.
 *    Hide episodes area (that only gets shown if they ask for episodes)
 */

async function searchForShowAndDisplay() {
  const term = $("#search-query").val();
  const shows = await getShowsByTerm(term);

  if (shows.length) {
    $episodesArea.hide(); // Hides the episdoes list div
    populateShows(shows);  // Populate the shows using the show data
    getEpisodesBtnTags();
    $showsList.show();
  } else {
    const alrtMsg = `"${term}" could not be found`
    AlertGenerator(alrtMsg);
    $showsList.hide();
  }
}


function AlertGenerator(msg) {
  const errDiv = $('#search_form_error');
  const $msg = $(`<span>${msg}</span>`)
  errDiv.append($msg);
  errDiv.show();

  setTimeout(function() {
    errDiv.html('');
    errDiv.hide();
  }, 1500)

}



$searchForm.on("submit", async function (evt) {
  evt.preventDefault();

  if (evt.target[0].value === '') {
    AlertGenerator('Please enter a search term')
    $showsList.hide();
  } else {
    await searchForShowAndDisplay();
  }
});

function getEpisodesBtnTags() {
  $(".Show-getEpisodes").on("click", async function(evt) {
    evt.preventDefault();

    console.log("Pressed Episde")
    const {showId, showName} = evt.target.parentNode.dataset;
    const episodes = await getEpisodesOfShow(showId);
    $searchFormDiv.hide();
    populateEpisodes(episodes, showName, showId);
  })
}


/** Write a clear docstring for this function... */

// Populates the Episode List
async function populateEpisodes(episodes, name, showId) { 
  $episodesList.empty();

  const { genres, summary, status } = await getShowsById(showId);;

  const edited_genres = genres.map( str => ' '.concat(str))

  

  $("#episodes_show_status").text(status);
  $("#episodes_show_summary").html(summary);
  $("#show-genres-id").text(edited_genres);
  
  $episodesTitle.text(`${name}`);

  for (let episode of episodes) {
    let image;
    ( !episode.image ) ? image = "" :  image = `<img class="mr-3 img-thumbnail episode-image" src=${episode.image.original}>`;
    const { name, season, number, airdate, summary } = episode;
    const $episode = $(
      `<li class="episode"> 
          ${image}
          <div class="episode-info"> 
            <h5> ${name} | Season ${season} Episode ${number} | ${airdate} </h5>
            <div>${!summary ? "" : summary}</div>
          </div>
      </li>`
    )
    $episodesList.append($episode);
  }


  $episodesArea.show();
  getShowFavBtnTags();
  $showsList.hide();
}


async function get_episodes_cast(id) {
  const episodes = await getEpisodesOfShow(id);
  
  for (let episode of episodes) {
    let image;
    ( !episode.image ) ? image = "" :  image = `<img class="mr-3 episode-image" src=${episode.image.original}>`;
    const { name, season, number, airdate, summary } = episode;
    const $episode = $(
      `<li class="episode p-3"> 
          ${image}
          <div class="episode-info"> 
            <h5> ${name} | Season ${season} Episode ${number} | ${airdate} </h5>
            <div>${!summary ? "" : summary}</div>
          </div>
      </li>`
    )
    $episodesList.append($episode);
  }
}


// Go Back Button on Episodes Page
$episodeListBack.on("click", function() {
  $episodesArea.hide();
  $episodesList.empty();
  $episodesTitle.text("");
  $showsList.show();
  $searchFormDiv.show();

})


// Server Side Comms

function getShowFavBtnTags() {
  const $showFavBtn = $(".Show-addToFav");
  $showFavBtn.on("click", function(evt) {
    // Send request to DB to add show to user fav list
    evt.preventDefault();


    // Toggle Heart Icon
      const heartIcon = evt.target.children[0].classList;
      heartIcon.toggle("fa-regular");
      heartIcon.toggle("fa-solid");
  
  })
}


async function fill_episode_details(sh_id) {
  const data = await getShowsById(sh_id)
  $("#episodes_show_status").text(data.status)
  $("#episodes_show_summary").html(data.summary)
}


$("#show_cast_btn").on("click", function(evt){ 
  evt.preventDefault();
  if (!$("#episodes-list").hasClass("hidden")) {
      $("#episodes-list").hide();
      $("#cast-list").show();
      $("#episodes-list").addClass("hidden");
      $("#show_cast_btn").text("Show Episodes")
  } else {
      $("#episodes-list").removeClass("hidden");
      $("#cast-list").hide();
      $("#episodes-list").show();
      $("#show_cast_btn").text("Show Cast")
  }
})



async function getRecommendations() {
      const $recommendations = $("#recommendation_list");
      $recommendations.empty();

      // Get a list of all the favorite actors
      const actor_ids = $(".favactor_id").map( function() {
          return $(this).text()
          }).get();
      
      const fav_shows_ids = $(".favshow_id").map( function() {
          return $(this).text()
          }).get();

      const favShowSet = new Set(fav_shows_ids);

      const rec_shows = new Set();

      let counter = 0;

      // Show 5 recommendations: Using the favorite actor, we will find which shows they have been in
      // Randomly select the shows favorite actors have been in and then save them to the rec_shows array
      while (counter < 5) {
          let rand_actor = actor_ids[Math.floor(Math.random() * actor_ids.length)];
          let actor_cast = await getActorCast(rand_actor);
          let sel_show = actor_cast[Math.floor(Math.random() * actor_cast.length)];

          let sel_show_id = sel_show._links.show.href.split('/').slice(-1)[0];
  
          if (!favShowSet.has(sel_show_id)) {
              rec_shows.add( sel_show_id );
              counter++
          }   
      }

      rec_shows.forEach( async show => {
          const showInfo = await axios.get(`http://api.tvmaze.com/shows/${show}`)
          const rec_show_list = $(`
          <li class="list-group-item w-25 border border-light mx-1" style="background-color: rgb(177, 192, 224); height: 18rem;">
              <div class="card h-100 card_profile">
                  <img src="${showInfo.data.image.original}" alt="${showInfo.data.name}" class="img-thumbnail profile-data-img">
                  <div class="card-body">
                      <h5 class="card-title">
                          <a href="/tvbuddy/shows/${showInfo.data.id}" style="text-decoration: none">
                              ${showInfo.data.name}
                          </a>
                      </h5>
                  </div>
              </div>
          </li>
          `)
          $recommendations.append(rec_show_list);
      })
  }


