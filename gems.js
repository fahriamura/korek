const fs = require('fs');
const axios = require('axios');

function readInitDataFromFile(filename) {
  const data = fs.readFileSync(filename, 'utf8');
  const initDataList = data.split('\n').map(line => line.trim()).filter(line => line !== '');
  return initDataList;
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
    console.log(response.data.token.access)
    return response.data.token.access;
  } catch (error) {
    console.error('Error during authentication:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function play(token) {
  try {
    const response = await axios.post(
      'https://game-domain.blum.codes/api/v1/game/play',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      }
    );

    const gameId = response.data.gameId;
    if (!gameId) {
      throw new Error('Game ID not found in response');
    }
    console.log('Game ID:', gameId);

    const claimResponse = await axios.post(
      'https://game-domain.blum.codes/api/v1/game/claim',
      {
        gameId,
        points: 150
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        }
      }
    );

    return claimResponse.data;
  } catch (error) {
    console.error('Error during play:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function misi(token) {
  try {
    const response = await axios.get('https://game-domain.blum.codes/api/v1/tasks', {
      headers: {
        Authorization: `Bearer ${token}`,
      }
    });

    for (const task of response.data) {
      await axios.post(
        `https://game-domain.blum.codes/api/v1/tasks/${task.id}/start`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          }
        }
      );

      await axios.post(
        `https://game-domain.blum.codes/api/v1/tasks/${task.id}/claim`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          }
        }
      );
    }

    return response.data;
  } catch (error) {
    console.error('Error during tasks execution:', error.response ? error.response.data : error.message);
    throw error;
  }
}

async function main() {
  const initDataList = readInitDataFromFile('./initdata.txt');
  console.log('InitData List:', initDataList);

  if (initDataList.length === 0) {
    console.error('No initData found in the file.');
    return;
  }

  const initData = initDataList[0];

  try {
    const token = await authenticate(initData);
    await play(token);
    await misi(token);
  } catch (error) {
    console.error('Error during initial task execution:', error.response ? error.response.data : error.message);

    try {
      const token = await authenticate(initData);
      await play(token);
      await misi(token);
    } catch (refreshError) {
      console.error('Error during reauthentication and task execution:', refreshError.response ? refreshError.response.data : refreshError.message);
    }
  }
}

main();
