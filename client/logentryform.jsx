/**
 * @jsx React.DOM
 */

var LogForm = React.createClass({
  handleSubmit: function() {
      var body = this.refs.body.getDOMNode().value;
      var tags = this.refs.tags.getDOMNode().value;
      this.props.onFormSubmit({body: body, tags: tags});

      return false; // prevents default action of the browser
  },

  render: function() {
    var body = "";
    var tags = "";
    console.log(this.props.entry);
    if (this.props.entry !== undefined) {
        body = this.props.entry.body;
        tags = this.props.entry.tags.map(function(tag) { return "#"+tag; }).join(', ');
    }

    var text = "";
    if (this.props.id !== undefined) {
        text = "Edit entry";
    } else {
        text = "New log entry";
    }

    return (
      <div className="logForm">
      {text}
        <form onSubmit={this.handleSubmit}>
          <dl>
            <dt>Body:</dt>
            <dd><textarea rows="20" cols="80" ref="body">{body}</textarea></dd>
            <dt>Tags:</dt>
            <dd><input type="text" size="50" value={tags} ref="tags" /></dd>
            <dd><input type="submit" value="Submit" /></dd>
          </dl>
        </form>
      </div>
    );
  }
});
