exports.handler = async (event) => {
    
    // Confirm the user
    event.response.autoConfirmUser = true;
    // Set the email as verified if it is in the request
    if (event.request.userAttributes.hasOwnProperty("email")) {
        event.response.autoVerifyEmail = true; //회원가입 - 사용자 확인, 이메일 검증 동시에
    }
    // Return to Amazon Cognito
    return event;
};

// exports.handler = async(event) => {
//     event.response.autoConfirmUser = true;
//     event.response.autoVerifyEmail = true;
//     return event;
// };