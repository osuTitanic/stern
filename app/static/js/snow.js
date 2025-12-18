const snowBuildUpCanvas = document.getElementById('snow-build-up');
const ctx = snowBuildUpCanvas.getContext('2d');
const snowflakes = [];

snowBuildUpCanvas.width = window.innerWidth;
snowBuildUpCanvas.height = document.documentElement.scrollHeight;

const snowflakeCharacters = ['❄', '*', '❉', '❃', '❅'];
const snowLevels = new Array(snowBuildUpCanvas.width).fill(0);
const maxSnowDepth = 40;

let snowflakeCounter = 0;
let snowflakeCreationRate;
let isMelting = false;

// Determine creation rate based on screen size
if (window.innerWidth > 768) {
    snowflakeCreationRate = 2; // More snowflakes on desktop
} else {
    snowflakeCreationRate = 8; // Fewer snowflakes on mobile
}

let lastFrameTime = performance.now();

function createSnowflake() {
    const snowflake = {
        x: Math.random() * snowBuildUpCanvas.width,
        y: -10,
        size: Math.random() * 20 + 10,
        speed: Math.random() * 1.5 + 1,
        opacity: 1,
        character: snowflakeCharacters[Math.floor(Math.random() * snowflakeCharacters.length)]
    };
    snowflakes.push(snowflake);
}

function smoothAccumulation() {
    // Smooth out the snow accumulation over time by averaging snow levels
    for (let i = 1; i < snowLevels.length - 1; i++) {
        snowLevels[i] = (snowLevels[i - 1] + snowLevels[i] + snowLevels[i + 1]) / 3;
    }
}

function drawSnowflakes(deltaTime) {
    ctx.clearRect(0, 0, snowBuildUpCanvas.width, snowBuildUpCanvas.height);

    // Draw buildup
    ctx.fillStyle = 'white';
    for (let x = 0; x < snowLevels.length; x++) {
        ctx.fillRect(x, snowBuildUpCanvas.height - snowLevels[x], 1, snowLevels[x]);
    }

    // Draw falling snowflakes
    ctx.fillStyle = 'white';
    snowflakes.forEach((snowflake, index) => {
        ctx.globalAlpha = snowflake.opacity;
        ctx.font = `${snowflake.size}px sans-serif`;
        ctx.fillText(snowflake.character, snowflake.x, snowflake.y);
        ctx.globalAlpha = 1;

        // Adjust speed by deltaTime
        snowflake.y += snowflake.speed * deltaTime * 60;

        // If snowflake reaches the bottom, accumulate snow
        if (
            snowflake.y + snowflake.size / 2 >=
            snowBuildUpCanvas.height - snowLevels[Math.floor(snowflake.x)]
        ) {
            const snowflakeX = Math.floor(snowflake.x);
            const snowflakeSize = snowflake.size / 2;

            // Accumulate snow more smoothly across a range with a weighted falloff effect
            const accumulationWidth = Math.ceil(snowflakeSize * 2);
            for (let i = -accumulationWidth; i <= accumulationWidth; i++) {
                const xIndex = Math.min(Math.max(snowflakeX + i, 0), snowLevels.length - 1);
                const distance = Math.abs(i); // The distance from the center of the snowflake
                const falloff = Math.exp(-distance / 5); // Gaussian falloff (smooth transition)

                // Apply the falloff to the accumulation to smooth the edges
                if (snowLevels[xIndex] < maxSnowDepth) {
                    snowLevels[xIndex] += snowflake.size / 4 * falloff; // Quicker accumulation with smoothing
                }
            }

            // Remove snowflake once it lands
            snowflakes.splice(index, 1);
        }
    });

    // Apply smoothing after every update
    smoothAccumulation();
}

function meltSnow() {
    let allMelted = true;
    for (let i = 0; i < snowLevels.length; i++) {
        if (snowLevels[i] > 0) {
            const meltRate = Math.random() * 0.3 + 0.1;
            snowLevels[i] -= meltRate;
            if (snowLevels[i] < 0) snowLevels[i] = 0;
            allMelted = false;
        }
    }

    // Introduce additional random offsets to simulate flow and uneven melting
    for (let i = 0; i < snowLevels.length; i++) {
        if (i > 0 && i < snowLevels.length - 1) {
            const leftNeighbor = snowLevels[i - 1];
            const rightNeighbor = snowLevels[i + 1];
            const average = (leftNeighbor + rightNeighbor) / 2;

            // Adjust current level slightly toward the average of neighbors
            const adjustment = (average - snowLevels[i]) * 0.2;
            snowLevels[i] += adjustment;
        }
    }

    return allMelted;
}

function checkFullSnow() {
    return snowLevels.every(level => level >= maxSnowDepth);
}

function animate() {
    const currentTime = performance.now();
    const deltaTime = (currentTime - lastFrameTime) / 1000;
    lastFrameTime = currentTime;

    if (!isMelting) {
        if (checkFullSnow()) {
            isMelting = true;
        } else if (snowflakeCounter % snowflakeCreationRate === 0) {
            createSnowflake();
        }
        snowflakeCounter++;
    } else {
      if (meltSnow()) {
        // Reset state when snow is fully melted
        snowflakes.length = 0;
        snowLevels.fill(0);
        isMelting = false;
      }
    }

    drawSnowflakes(deltaTime);
    requestAnimationFrame(animate);
}

// Update array on window resize
window.addEventListener('resize', () => {
    snowBuildUpCanvas.width = window.innerWidth;
    snowBuildUpCanvas.height = document.documentElement.scrollHeight;
    snowLevels.fill(0);
});

animate();
