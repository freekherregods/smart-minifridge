'use strict';

const handleData = function (url, callbackFunctionName, callbackErrorFunctionName = null, method = 'GET', body = null) {
  fetch(url, {
    method: method,
    body: body,
    headers: {
      'content-type': 'application/json',
    },
  })
    .then(function (response) {
      if (!response.ok) {
        console.warn(`>> Probleem bij de fetch(). Statuscode: ${response.status}`);
        if (callbackErrorFunctionName) {
          console.warn(`>> Callback errorfunctie ${callbackErrorFunctionName.name}(response) wordt opgeroepen`);
          callbackErrorFunctionName(response);
        } else {
          console.warn('>> Er is geen callback errorfunctie meegegeven als parameter');
        }
      } else {
        return response.json();
      }
    })
    .then(function (jsonObject) {
      if (jsonObject) {
        callbackFunctionName(jsonObject);
      }
    });
  /*.catch(function(error) {
      console.warn(`>>fout bij verwerken json: ${error}`);
      if (callbackErrorFunctionName) {
        callbackErrorFunctionName(undefined);
      }
    })*/
};
