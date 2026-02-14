/**
 * Keyboard shortcuts overlay panel.
 */

export function KeyboardOverlay() {
  function handleOverlayClick(e) {
    if (e.target === e.currentTarget) {
      e.currentTarget.classList.remove("open");
    }
  }

  function handleHintClick() {
    document.getElementById("kbdOverlay").classList.toggle("open");
  }

  return (
    <>
      <div class="kbd-hint" onClick={handleHintClick}>? shortcuts</div>
      <div class="kbd-overlay" id="kbdOverlay" onClick={handleOverlayClick}>
        <div class="kbd-overlay-panel">
          <h3>Keyboard Shortcuts</h3>
          <div><span>Switch tabs</span><kbd>1</kbd>-<kbd>5</kbd></div>
          <div><span>Search files</span><kbd>/</kbd></div>
          <div><span>Move selection</span><kbd>j</kbd> / <kbd>k</kbd></div>
          <div><span>Open selected</span><kbd>Enter</kbd></div>
          <div><span>Go back</span><kbd>Esc</kbd></div>
          <div><span>Toggle shortcuts</span><kbd>?</kbd></div>
        </div>
      </div>
    </>
  );
}
