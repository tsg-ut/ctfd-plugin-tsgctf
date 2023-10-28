// HACK: We want to keep CTFd repository untouched as possible.
// So we edit DOM of admin page by this script.
// Note that this script only works on admin page,
// therefore dirty hack would be acceptable.

const submitBadge = async (challengeId, badgeUrl, method) => {
  // HACK: Get CSRF token from global variable `init`
  // eslint-disable-next-line no-undef
  if (init) {
    // eslint-disable-next-line no-undef
    const csrf = init.csrfNonce;
    const ep = `/api/v1/challenges/${challengeId}/badge`;
    return await fetch(ep, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Csrf-Token': csrf,
      },
      body: JSON.stringify({
        badge_url: badgeUrl,
      }),
    });
  }
}

const getBadge = async (challengeId) => {
  const ep = `/api/v1/challenges/${challengeId}/badge`;
  return fetch(ep, {
    method: "GET",
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((res) => {
    if (res.ok)
      return res.json();
    else
      return null;
  }).catch(() => {
    return null;
  });
}

const doAddBadgeForm = ($form, defaultValue, submitCallback) => {
  const innerHTML = `
  <div class="form-group" id="form-tsg-badge">
    <label>
      Badge URL:<br>
      <small class="form-text text-muted">
        Status badge endpoint. Leave empty to disable.
      </small>
    </label>
    <input type="text" class="form-control tsgctf_badge_url" value="${defaultValue}">
  </div>
  `;

  const submitHook = async () => {
    submitCallback();
  };
  $form.submit(submitHook);

  $form.find('button[type="submit"]').parent().before(innerHTML)
}

const addBadgeFormEntryNew = ($form) => {
  const challengeIdInput = $('input#challenge_id');
  const observer = new MutationObserver((mutations) => {
    mutations.forEach(async (mutation) => {
      if (mutation.attributeName === 'value') {
        const challengeId = challengeIdInput.val();
        const badgeUrl = $form.find('input.tsgctf_badge_url').val();
        if (challengeId !== '') {
          const res = await submitBadge(challengeId, badgeUrl, "POST");
          if (res.status !== 200) {
            console.error(`Failed to submit badge: ${res.status}`);
            alert(`Failed to submit badge: ${res.status}`)
          }
        }
      }
    });
  });

  doAddBadgeForm($form, '', () => {
    observer.observe(challengeIdInput[0], { attributes: true });
  })
}

const hookChallengeNewPage = () => {
  const divCreateChalEntry = $('#create-chal-entry-div');
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        for (const addedNode of mutation.addedNodes) {
          if (addedNode.nodeName === 'FORM') {
            addBadgeFormEntryNew($(addedNode));
          }
        }
      }
    });
  });
  observer.observe(divCreateChalEntry[0], { childList: true });
}

const addBadgeFormEntryEdit = async ($form) => {
  const challengeId = window.location.pathname.split('/')[3];
  const res = await getBadge(challengeId);
  if (res === null) {
    alert('Failed to get badge info');
    return;
  }
  const badgeUrl = res.badge_url;

  doAddBadgeForm($form, badgeUrl || '', async () => {
    const newBadgeUrl = $('input.tsgctf_badge_url').val();
    const res = await submitBadge(challengeId, newBadgeUrl, "PATCH");
    if (res.status !== 200) {
      console.error(`Failed to submit badge: ${res.status}`);
      alert(`Failed to submit badge: ${res.status}`)
    }
  })
}

const hookChallengeEditPage = () => {
  addBadgeFormEntryEdit($('#challenge-update-container'));
}

$(document).ready(() => {
  if (window.location.pathname === '/admin/challenges/new') {
    hookChallengeNewPage();
  } else if (window.location.pathname.startsWith('/admin/challenges/')) {
    const challengeId = window.location.pathname.split('/')[3];
    if (challengeId.match(/^\d+$/)) {
      hookChallengeEditPage();
    }
  }
});
