
const startbutton = document.getElementById('start-button');
let buttons = document.querySelectorAll('button');
let squres = ['red','green','blue','yellow'];
let highestLevel = 0;
let level = 0;
let playerPattern = [];
let timeoutIds = [];


buttons.forEach(button => {
    if (button.id !== 'start-button' && button.id !== 'play-again-button') {
        button.addEventListener('click', playerPatternFunc);
    }
});

function startGame() {
    level = 1;
    playerPattern = [];
    pattern =[];
    let startHtml = document.getElementById('start');
    let set1Html = document.getElementById('set1');
    set1Html.style.display = 'flex';
    let set2Html = document.getElementById('set2');
    set2Html.style.display = 'flex';
    let highestlevelHtml = document.getElementById('highestlevel');
    let levelHtml = document.getElementById('level');
    startHtml.style.display = 'none';
    highestlevelHtml.style.display = 'flex';
    levelHtml.style.display = 'flex';
    randomPattern()
}

function playerPatternFunc() {
    let squrechoose = this.id;
    playerPattern.push(squrechoose)
    if (playerPattern.length === pattern.length) {
        console.log('user array' + playerPattern)
        console.log(level)
        checkPatterns(playerPattern)
    }
}

function checkPatterns(playerPattern) {
    let matching = true;
    for (i=0; i<playerPattern.length; i++) {
        if (playerPattern[i] !== pattern[i]) {
            matching = false;
        }
    }
    if (matching == true) {
        playerPattern = [];
        console.log("its a match");
        level += 1;
        nextLevel()


    } else {


        gameOver()
    }
} 


function randomPattern() {
let randomIndex = Math.floor(Math.random() * squres.length);
let randomSqure = squres[randomIndex];
pattern.push(randomSqure);
console.log('random array' + pattern);
showPattern(pattern);
}

function showPattern(pattern) {
    let delay = 800;
    timeoutIds = [];
    for (let i = 0; i < pattern.length; i++) {
        let timeoutId = setTimeout(() => {
            flashButton(pattern[i]);
            makesound(pattern[i]); 
        }, delay);
        timeoutIds.push(timeoutId);
        delay += 800;
    }
}

function nextLevel() {
    playerPattern = []
    let levelHtml = document.getElementById('level')
    levelHtml.innerHTML = 'Level:' + level
    randomPattern()
}

function gameOver() {
    var gameoversound = new Audio('static/sounds/gameover.mp3')
    gameoversound.play();
    let container = document.getElementById('simoncontainer');
    let gameover = document.getElementById('gameover');
    container.style.display = 'none';
    gameover.style.display = 'flex';
    timeoutIds.forEach(id => clearTimeout(id));
    timeoutIds = [];
}

function flashButton(color) {
    let button= document.getElementById(color)
    button.style.backgroundColor = 'white';
    setTimeout(() => {
        button.style.backgroundColor = color;
    }, 500); 
}


function playAgain() {
    let container = document.getElementById('simoncontainer');
    let gameover = document.getElementById('gameover');
    container.style.display = 'flex';
    gameover.style.display = 'none';
    let playerLevel = level - 1;
    if ( playerLevel > highestLevel) {
        highestLevel = playerLevel;
        let highestLevelHtml = document.getElementById('highestlevel')
        highestLevelHtml.innerHTML = 'Highest Level:' + playerLevel
        alert("You achieved a new record! Well done")
    }
    level = 1;
    let levelHtml = document.getElementById('level')
    levelHtml.innerHTML = 'Level:' + level

    timeoutIds.forEach(id => clearTimeout(id));
    timeoutIds = [];
    startGame()
}


for (var i=0; i<document.querySelectorAll(".squre").length; i++) {
    document.querySelectorAll("button")[i+1].addEventListener("click", function () {
        var squrechoose = this.classList[0];
       console.log(squrechoose)
       makesound(squrechoose)
    });
}


function makesound(squrechoose) {
    switch (squrechoose) {
        case "blue":
            var blue = new Audio('static/sounds/blue.mp3')
            blue.play();
            break;

        case "green":
            var green = new Audio('static/sounds/green.mp3')
            green.play();
            break;
            
        case "red":
            var red = new Audio('static/sounds/red.mp3')
            red.play();
            break;

        case "yellow":
            var yellow = new Audio('static/sounds/yellow.mp3')
            yellow.play();
            break;

        default:
            console.log("default");
            break;
    }
}