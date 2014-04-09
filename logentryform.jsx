/**
 * @jsx React.DOM
 */

var LogForm = React.createClass({
  render: function() {
    var body = "";
    var tags = "";
    if (this.props.entry !== undefined) {
        body = this.props.entry.body;
        tags = this.props.entry.tags;
    }

    return (
      <div className="logForm">
        New log entry:
        <form>
          <dl>
            <dt>Body:</dt>
            <dd><textarea name="body" rows="20" cols="80">{body}</textarea></dd>
            <dt>Tags:</dt>
            <dd><input type="text" size="50" name="tags" value={tags} /></dd>
            <dd><input type="submit" value="Submit" /></dd>
          </dl>
        </form>
      </div>
    );
  }
});
