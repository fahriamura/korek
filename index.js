const fs = require('fs');
const axios = require('axios');

async function readInitDataFromFile(filename) {
  return new Promise((resolve, reject) => {
    fs.readFile(filename, 'utf8', (err, data) => {
      if (err) {
        reject('Error reading file: ' + err);
      } else {
        const initDataList = data.split('\n').map(line => line.trim()).filter(line => line !== '');
        resolve(initDataList);
      }
    });
  });
}

async function authenticate(initData) {
  try {
    const response = await axios.post(
      'https://gateway.blum.codes/v1/auth/provider/PROVIDER_TELEGRAM_MINI_APP',
      { query: initData },
      {
        headers: {
          'accept-language': 'en-US,en;q=0.9,id;q=0.8',
          'origin': 'https://telegram.blum.codes',
          'priority': 'u=1, i',
          'referer': 'https://telegram.blum.codes/',
          'sec-ch-ua': '"Microsoft Edge";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
          'sec-ch-ua-mobile': '?0',
          'sec-ch-ua-platform': '"Windows"',
          'sec-fetch-dest': 'empty',
          'sec-fetch-mode': 'cors',
          'sec-fetch-site': 'same-site',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
        },
      }
    );
    return response.data.token.access;
  } catch (error) {
    console.error('Error during authentication:', error);
    throw error;
  }
}



async function getClaim(token) {
  try {
    const response = await axios.post(
      'https://game-domain.blum.codes/api/v1/farming/claim',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    console.log('Claim successful');
    startFarm(token);
  } catch (error) {
    console.log('Claim not available:', error.response.data.message);
    startFarm(token);
  }
}

async function startFarm(token) {
  try {
    const response = await axios.post(
      'https://game-domain.blum.codes/api/v1/farming/start',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    console.log(response.data);
    setTimeout(() => getBalance(token));
  } catch (error) {
    console.log('Error during start farming:', error.response);
  }
}

async function getBalance(token) {
  try {
    const response = await axios.get(
      'https://game-domain.blum.codes/api/v1/user/balance',
      {
        headers: {
          Accept: 'application/json, text/plain, */*',
          'Accept-Encoding': 'gzip, deflate, br, zstd',
          'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
          Authorization: `Bearer ${token}`,
          Origin: 'https://telegram.blum.codes',
          Priority: 'u=1, i',
          Referer: 'https://telegram.blum.codes/',
          'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
          'Sec-Ch-Ua-Mobile': '?0',
          'Sec-Ch-Ua-Platform': '"Windows"',
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Site': 'same-site',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        },
      }
    );
    console.log('Balance:', response.data.availableBalance);
    scheduleClaimAndRefresh(token, response.data.farming.endTime);
  } catch (error) {
    console.log('Error fetching balance:', error);
  }
}

function scheduleClaimAndRefresh(token, endTimeUnix) {
  const endTimeDate = new Date(endTimeUnix);
  const now = new Date();
  const timeDifference = endTimeDate.getTime() - now.getTime();
  let timeDifferenceInMinutes = Math.ceil(timeDifference / (1000 * 60));

  const timerInterval = setInterval(() => {
    if (timeDifferenceInMinutes <= 0) {
      clearInterval(timerInterval);
      console.log('Time to claim!');
      return;
    }
    console.log(`Time left to claim: ${timeDifferenceInMinutes} minutes`);
    timeDifferenceInMinutes--;
  }, 60 * 60 * 1000);

  setTimeout(() => getClaim(token), timeDifference);
  console.log('Next claim in:', timeDifferenceInMinutes, 'minutes');

  const refreshInterval = 30 * 60 * 1000;
  setTimeout(() => refreshToken(token), refreshInterval);
  console.log('Token will be refreshed in 30 minutes');

  let countdownTime = refreshInterval;
  const refreshCountdownInterval = setInterval(() => {
    if (countdownTime <= 0) {
      clearInterval(refreshCountdownInterval);
      console.log('Token has been refreshed!');
      return;
    }
    const remainingMinutes = Math.floor(countdownTime / 60000);
    if (countdownTime % 60000 === 0) {
      console.log(`Time left for token refresh: ${remainingMinutes} minutes`);
    }
    countdownTime -= 1000;
  }, 60 * 1000);
}

async function refreshToken(token) {
  try {
    const response = await axios.post(
      'https://gateway.blum.codes/v1/auth/refresh',
      { refresh: token },
    );
    const newToken = response.data.access;
    console.log('Token refreshed:', newToken);
    getClaim(newToken);
  } catch (error) {
    console.log('Error refreshing token:', error.response.data);
  }
}

(async () => {
  try {
    const initDataList = await readInitDataFromFile('./initdata.txt');
    console.log('InitData List:', initDataList);

    const tasks = initDataList.map(async initData => {
      try {
        const token = await authenticate(initData);
        await getClaim(token);
      } catch (error) {
        console.error('Error during getClaim:', error);
        try {
          const token = await authenticate(initData);
          await refreshToken(token);
        } catch (error) {
          console.error('Error during refreshToken:', error);
        }
      }
    });

    await Promise.all(tasks);
  } catch (error) {
    console.error('Error in main flow:', error);
    exec('node index.js', (err, stdout, stderr) => {
      if (err) {
        console.error(`Exec error: ${err}`);
        return;
      }
      console.log(`Stdout: ${stdout}`);
      console.error(`Stderr: ${stderr}`);
    });
  }
})();
