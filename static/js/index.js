
let stories; // This will contain three(?) stories for the current participant. 
let storyIdx = 0; // Index number of the current story 

$.ready(()=>{
  $(".page").addClass("hidden");
  $(".intro").removeClass("hidden");
});

function ajaxGet(reqJson, callback){
  /* Example usage. 
    ajaxGet({"action":"add", "JSON":JSON.stringify({'a':1234,'b':234})})
  */
    $.getJSON('ajaxGet',reqJson, callback);
}

function fetchStories(){
  // This method will be called once, when a new participant begins
  ajaxGet({
    "action":"fetchStories"
  }, (data)=>{
    stories = data.stories;
  });
}

function renderStoryAndQuestion(si) {
  // For the given story index (si), it renders the story and question in the corresponding div
  $(".story_content").html(stories(si).story.html);
  $(".quiz_content").html(stories(si).quiz.html);

  // Showing the story page only
  $(".page").addClass("hidden");
  $(".story").removeClass("hidden");
}

function proceedToQuiz() {
  $(".page").addClass("hidden");
  $(".quiz").removeClass("hidden");
}

function proceedToNextStory(){
  storyIdx++;
  if (storyIdx == stories.length) {
    proceedToPostQuestionnaire();
  } else {
    renderStoryAndQuestion(storyIdx);
  }
}

function proceedToPostQuestionnaire() {
  $(".page").addClass("hidden");
  $(".post").removeClass("hidden");
}

function proceedToBye() {

}

function log(e) {
  if(e=="start") {
    // Pressing Start button
    let jsonString = JSON.stringify({
      "event":"Start Button"
    });
    ajaxGet({
      "action":"add",
      "JSON":jsonString
    }, (data)=>{
      console.log(data);
    });
  } else if(e=="a specific event") {
    // DEFINE WHAT TO LOG
  } else if(e=="another specific event") {
    // DEFINE WHAT TO LOG
  } 
}