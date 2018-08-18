exports.handler = function(event, context, callback) {
  console.log("Hello " + event.key1 + "!");
  callback(null, "some success message");
}