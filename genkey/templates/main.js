

//stock var

// To send to the CryptoAPI
let matricule1;
let matricule2;
let time1;
let time2;
let distance;

// What genKey returns us
let secretKey;
let publicContext;

// What CryptoAPI returns us == what we send to the server
let encMatricule1;
let encMatricule2;
let encTime1;
let encTime2;
let modifiedDistance;

// what the service gives us
let encResultMult;
let invSpeed;

// for yolo
let image_encoded64_1;
let image_encoded64_2;

let allowCrossDomain = function (req, res, next) {
    res.header('Access-Control-Allow-Origin', "*");
    res.header('Access-Control-Allow-Headers', "*");
    next();
}
//   app.use(allowCrossDomain);












function readFile1() {

    if (!this.files || !this.files[0]) return;

    const FR = new FileReader();

    FR.addEventListener("load", function (evt) {
        document.querySelector("#img2").src = evt.target.result;
        document.querySelector("#b64").innerHTML = evt.target.result;
        // document.getElementById("#b64") = evt.target.result;
        image_encoded64_2 = evt.target.result;// additional info + base64  

        image_encoded64_2 = image_encoded64_2.replace('data:image/png;base64,', ''); //here I have my base64image

        image_encoded64_2 = image_encoded64_2.replace('data:image/jpeg;base64,', ''); //here I have my base64image




    });

    FR.readAsDataURL(this.files[0]);

}

document.querySelector("#inp2").addEventListener("change", readFile1);

// upload and convert to base64









function readFile2() {

    if (!this.files || !this.files[0]) return;

    const FR = new FileReader();

    FR.addEventListener("load", function (evt) {
        document.querySelector("#img1").src = evt.target.result;
        document.querySelector("#b64").innerHTML = evt.target.result;
        // document.getElementById("#b64") = evt.target.result;
        image_encoded64_1 = evt.target.result;// additional info + base64
        image_encoded64_1 = image_encoded64_1.replace('data:image/png;base64,', ''); //here I have my base64image
        image_encoded64_1 = image_encoded64_1.replace('data:image/jpeg;base64,', ''); //here I have my base64image
    });

    FR.readAsDataURL(this.files[0]);

}

document.querySelector("#inp1").addEventListener("change", readFile2);





// detect and get the plate number from an image
apiYoloUrl = '/inference_yolo';
function yolo1() {
    const dataToSend = {
        "image_base64_1": image_encoded64_1,
        "image_base64_2": image_encoded64_2

    }


    // use the encrypt endpoint of the API crypto
    fetch(apiYoloUrl, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(dataToSend)
    })

        .then(response => response.json())
        .then(function (json) {
            json => console.log(json)
            matricule1 = json["registration_number_1"]
            matricule2 = json["registration_number_2"]


            document.getElementById('regi1').innerText = "The First registration number is "+ matricule1;
            document.getElementById('regi2').innerText = "The Second registration number is "+ matricule2;

            // document.getElementsByName("Image1")[0].src = resYolo
            // document.getElementById('info_enc_mat_2').innerText = "The size of the encrypted second registration number is : " + encMatricule2.length;

        })
        .catch(err => console.log('Request Failed', err))

}

// get the value of mat_1&2 and t_1&2 and d after submitting
let form = document.getElementById('submit_encrypt')
form.addEventListener('submit', function (event) {
    event.preventDefault() // to prevent from auto-submit

    // matricule1 = document.getElementById('mat_1').value
    // matricule2 = document.getElementById('mat_2').value
    time1 = document.getElementById('t_1').value
    time2 = document.getElementById('t_2').value
    distance = document.getElementById('d').value
})




const container = document.querySelector('.container');
const loadGenKey = document.querySelector('.load-tuts');

api_KeyGen_url = '/Key_Generation';
function GenKey() {
    fetch(api_KeyGen_url)
        .then(response => response.json())
        .then(function (json) {
            json => console.log(json)
            secretKeyBfv = json['secret_key_bfv'];
            publicContextBfv = json["public_context_bfv"];

            secretKeyCkks = json['secret_key_ckks'];
            publicContextCkks = json["public_context_ckks"];

            document.getElementById('key_info').innerText = "The Key generation have been done !"
        })
        .catch(err => console.log('Request Failed', err))
}








// crypté l'image avec le contexte public
api_crypto_endpoint_enc = '/encrypt';
function crypto() {
    
    const dataToSend = {
        "matricule1": matricule1,
        "matricule2": matricule2,
        "time1": time1,
        "time2": time2,
        "distance": distance,
        "context_public_bfv": publicContextBfv,
        "context_public_ckks": publicContextCkks
    }


    // use the encrypt endpoint of the API crypto
    fetch(api_crypto_endpoint_enc, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(dataToSend)
    })

        .then(response => response.json())
        .then(function (json) {
            json => console.log(json)
            encMatricule1 = json["enc_matricule_1"];
            encMatricule2 = json["enc_matricule_2"];
            encTime1 = json["enc_time_1"];
            encTime2 = json["enc_time_2"];
            modifiedDistance = json["distance"];


            document.getElementById('info_enc_mat_1').innerText = "The size of the first encrypted registration number is : \n" + encMatricule1.length;
            document.getElementById('info_enc_mat_2').innerText = "The size of the encrypted second registration number is : " + encMatricule2.length;

        })
        .catch(err => console.log('Request Failed', err))

}



//faire l'inference 
api_infenrece = '/inference';
function Inference() {

    const dataToSend = {

        "mat_1_seri_bytes": encMatricule1,
        "mat_2_seri_bytes": encMatricule2,
        "t_1_seri_bytes": encTime1,
        "t_2_seri_bytes": encTime2,
        "dist": modifiedDistance,
        "context_public_bfv": publicContextBfv,
        "context_public_ckks": publicContextCkks
    }

    fetch(api_infenrece, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(dataToSend)
    }, { mode: 'no-cors' }
    )

        .then(response => response.json())
        .then(function (json) {
            json => console.log(json)
            encResultMult = json["res_mult"];
            invSpeed = json["inverse_speed"];
            let inferenceTime = json["inference_time"]
            document.getElementById('inf_time').innerText = "The inference time  is :" + inferenceTime;
        })
        .catch(err => console.log('Request Failed', err));
}

// some preprocess before decrypt

  
api_decrypt_endpoint = '/decrypt';
function decrypt() {
    const dataToSend = {
        "res_enc": encResultMult,
        "inv_speed": invSpeed,
        "secret_context_bfv": secretKeyBfv,
        "secret_context_ckks": secretKeyCkks,
    }


    // use the encrypt endpoint of the API crypto
    fetch(api_decrypt_endpoint, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "POST",
        body: JSON.stringify(dataToSend)
    })

        .then(response => response.json())
        .then(function (json) {
            json => console.log(json)
            let speed = json["vehicule_speed"]
            let count = json["res_mult"]

            if (count == matricule1.length && count == matricule2.length ){
                document.getElementById('same_registration_number').innerText = "These are the same registration number \n and the speed is : " + speed.toFixed(2) + "km/h";
            } else {
                document.getElementById('diff_registration_number').innerText = "These are not the same Registration Number";
            }

            


        })
        .catch(err => console.log('Request Failed', err))

}
